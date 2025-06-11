window.addEventListener('DOMContentLoaded', () => {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const fileListDiv = document.getElementById('fileList');
    let files = [];

    function renderFileList() {
        fileListDiv.innerHTML = '';
        files.forEach((file, idx) => {
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item';

            const infoDiv = document.createElement('div');
            infoDiv.className = 'file-info';

            const nameDiv = document.createElement('div');
            nameDiv.className = 'file-name';
            nameDiv.textContent = file.name;

            // 不再创建 metaDiv 和 statusSpan
            infoDiv.appendChild(nameDiv);

            const removeBtn = document.createElement('span');
            removeBtn.className = 'file-remove';
            removeBtn.innerHTML = '&times;';
            removeBtn.title = '移除';
            removeBtn.onclick = () => {
                files.splice(idx, 1);
                renderFileList();
            };

            fileItem.appendChild(infoDiv);
            fileItem.appendChild(removeBtn);

            fileListDiv.appendChild(fileItem);
        });
    }

    // 点击上传区域，触发文件选择
    uploadArea.addEventListener('click', () => fileInput.click());

    // 拖拽高亮
    uploadArea.addEventListener('dragover', e => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });
    uploadArea.addEventListener('dragleave', e => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
    });
    uploadArea.addEventListener('drop', e => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        handleFiles(e.dataTransfer.files);
    });

    // 文件选择
    fileInput.addEventListener('change', e => {
        handleFiles(e.target.files);
    });

    function handleFiles(selectedFiles) {
        for (let file of selectedFiles) {
            // 只允许 PDF、DOC、DOCX
            if (!/(\.pdf|\.docx?)$/i.test(file.name)) continue;
            // 防止重复
            if (files.find(f => f.name === file.name && f.size === file.size)) continue;
            files.push(file);
        }
        renderFileList();
    }

    // 表头动态输入
    const headersContainer = document.getElementById('headersContainer');
    const addHeaderBtn = document.getElementById('addHeaderBtn');

    function addHeaderInput(value = '') {
        const card = document.createElement('div');
        card.className = 'header-card';

        const input = document.createElement('input');
        input.type = 'text';
        input.className = 'header-input';
        input.placeholder = '新表头';
        input.value = value;

        input.oninput = function() {
            input.style.color = input.value.trim() ? '#222' : '#aaa';
        };
        input.style.color = value ? '#222' : '#aaa';

        const remove = document.createElement('span');
        remove.className = 'header-remove';
        remove.innerHTML = '&times;';
        remove.title = '移除';
        remove.onclick = () => {
            headersContainer.removeChild(card);
        };

        card.appendChild(input);
        card.appendChild(remove);

        // 插入到加号按钮前面
        headersContainer.insertBefore(card, addHeaderBtn);
    }

    addHeaderBtn.onclick = () => addHeaderInput();

    // 默认添加两个表头输入
    addHeaderInput('文件名');
    addHeaderInput('研究方法');

    // 运行处理
    document.getElementById('runBtn').onclick = () => {
        if (files.length === 0) {
            showMsg('请先选择文件');
            return;
        }
        const headerInputs = headersContainer.querySelectorAll('.header-input');
        const headers = Array.from(headerInputs).map(input => input.value.trim()).filter(Boolean);
        if (headers.length === 0) {
            showMsg('请填写至少一个表头');
            return;
        }
        // 先上传文件
        const formData = new FormData();
        files.forEach(f => formData.append('files', f));
        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            if (data.error) {
                showMsg('上传失败: ' + data.error);
                return;
            }
            // 上传成功后再请求处理
            return fetch('/generate_excel', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ headers })
            });
        })
        .then(res => res && res.json())
        .then(data => {
            if (!data) return;
            if (data.error) showMsg('运行失败: ' + data.error);
            else showMsg('处理完成');
        })
        .catch(() => showMsg('上传或处理出错'));
    };

    // 查看结果
    document.getElementById('resultBtn').onclick = () => {
        fetch('/result')
        .then(res => res.json())
        .then(data => {
            if (data.error) {
                showMsg('未找到结果: ' + data.error);
                return;
            }
            renderTable(data);
            showMsg('结果已展示');
        })
        .catch(() => showMsg('获取结果出错'));
    };

    // 下载Excel
    document.getElementById('downloadBtn').onclick = () => {
        window.open('/download', '_blank');
    };

    function showMsg(msg) {
        document.getElementById('msg').innerText = msg;
    }

    function renderTable(data) {
        const table = document.getElementById('result-table');
        table.innerHTML = '';
        if (!Array.isArray(data) || data.length === 0) {
            table.innerHTML = '<tr><td>无数据</td></tr>';
            return;
        }
        const header = Object.keys(data[0]);
        let thead = '<tr>' + header.map(h => `<th>${h}</th>`).join('') + '</tr>';
        let rows = data.map(row => '<tr>' + header.map(h => `<td>${row[h]}</td>`).join('') + '</tr>').join('');
        table.innerHTML = thead + rows;
    }
});