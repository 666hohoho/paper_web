//API相关--------------------------------------------------------------------------
function showAPIPopup() {
    document.getElementById('api-popup').style.display = 'block';
    document.getElementById('apiTypeInput').value = apiConfig.Type;
    document.getElementById('apiHostInput').value = apiConfig.host;
    document.getElementById('apiKeyInput').value = apiConfig.key;
}

function testConnection() {
    // 获取输入框的值
    const apiType = document.getElementById('apiTypeInput').value; 
    const apiHost = document.getElementById('apiHostInput').value;
    const apiKey = document.getElementById('apiKeyInput').value;

    // 发送请求到后端
    fetch('/test_connection', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            api_type: apiType,
            api_host: apiHost,
            api_key: apiKey
        })
    })
    .then(response => response.json())
    .then(data => {
        // 显示测试结果
        const msgDiv = document.getElementById('msg');
        if (data.success) {
            msgDiv.textContent = '连接成功！';
            msgDiv.style.color = 'green';
        } else {
            msgDiv.textContent = '连接失败：' + (data.message || '未知错误');
            msgDiv.style.color = 'red';
        }
    })
    .catch(error => {
        const msgDiv = document.getElementById('msg');
        msgDiv.textContent = '请求出错：' + error;
        msgDiv.style.color = 'red';
    });
}

document.getElementById('close-api-popup').addEventListener('click', function() {
        document.getElementById('api-popup').style.display = 'none';
    });



//上传文件---------------------------------------------------------------------------
// 绑定 change 事件监听器
let files = [];
document.getElementById('fileInput').addEventListener('change', async (event) => {
    const fileInput = event.target;
    const files = fileInput.files;
    if (!files || files.length === 0) {
        console.error('No files selected');
        return;
    }

    const formData = new FormData();

    // 遍历所有文件并添加到 FormData
    for (let i = 0; i < files.length; i++) {
        formData.append(`file_${i}`, files[i]); // 使用唯一键名
    }

    // 调试输出 FormData 的内容
    for (let [key, value] of formData.entries()) {
        console.log(`${key}:`, value);
    }

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData,
        });

        if (response.ok) {
            console.log('Files uploaded successfully');
        } else {
            console.error('Failed to upload files:', await response.json());
        }
    } catch (error) {
        console.error('Error uploading files:', error);
    }
    
    // 处理文件列表显示
    const fileListDiv = document.getElementById('fileList');
    // 不清空，直接追加
    for (let i = 0; i < files.length; i++) {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        fileItem.textContent = files[i].name;

        // 添加删除按钮
        const deleteButton = document.createElement('button');
        deleteButton.textContent = '删除';
        deleteButton.className = 'delete-button';

        // 将文件名绑定到按钮的自定义属性
        deleteButton.setAttribute('data-file-name', files[i].name);

        deleteButton.onclick = async (event) => {
            try {
                // 从按钮的自定义属性中获取文件名
                const fileName = event.target.getAttribute('data-file-name');
                console.log('Deleting file:', fileName);

                // 发送删除请求到后端
                const response = await fetch('/delete', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ filename: fileName }), // 使用后端匹配的键名
                });

                if (response.ok) {
                    console.log(`File ${fileName} deleted successfully`);
                    fileListDiv.removeChild(fileItem); // 删除文件项
                } else {
                    const errorResponse = await response.json();
                    console.error(`Failed to delete file ${fileName}:`, errorResponse);
                }
            } catch (error) {
                console.error(`Error deleting file ${fileName}:`, error);
            }
        };

        fileItem.appendChild(deleteButton);
        fileListDiv.appendChild(fileItem);
    }
    // 清空 input，否则连续选同一文件不会触发 change 事件
    event.target.value = '';
});


// 点击按钮触发文件选择
function handleFileUpload() {
    const fileInput = document.getElementById('fileInput');
    fileInput.click();
}

function onFileSelected(event) {
    const file = event.target.files[0];
    if (file) {
        console.log('选择的文件:', file);
    }
}





//添加字段----------------------------------------------------------------------------
function showFieldsIn() {
        const headersContainer = document.getElementById('headersContainer');
        headersContainer.style.display = headersContainer.style.display = 'block' ;
    }

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

document.getElementById('close-fields-popup').addEventListener('click', function() {
        document.getElementById('headersContainer').style.display = 'none';
    });


// 运行处理----------------------------------------------------------------------------
document.getElementById('runBtn').addEventListener('click', function ()  {
    const apiType = document.getElementById('apiTypeInput').value.trim();
    const apiKey = document.getElementById('apiKeyInput').value.trim();
    const apiHost = document.getElementById('apiHostInput').value.trim();
    const headerInputs = headersContainer.querySelectorAll('.header-input');
    const headers = Array.from(headerInputs).map(input => input.value.trim()).filter(Boolean);
    console.log('API Type:', apiType);
    console.log('API Key:', apiKey);
    console.log('API Host:', apiHost);
    console.log('Headers:', headers);

    if (!apiKey || !apiHost || headers.length === 0) {
        console.log('请填写所有必填项');
        return;
    } 
    // 请求后端处理
    fetch('/generate_excel', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ headers, api_type: apiType, api_key: apiKey, api_host: apiHost })
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            showMsg('运行失败: ' + data.error);
        } else {
            showMsg('处理完成: ' + data.message);
        }
    })
    .catch(() => showMsg('运行出错'));
});


// 查看结果----------------------------------------------------------------------------
document.getElementById('resultBtn').onclick = () => {
    fetch('/result')
        .then(res => res.json())
        .then(data => {
            if (data.error) {
                showMsg('未找到结果: ' + data.error);
                return;
            }
            renderTable(data); // 渲染表格
            showMsg('结果已展示');
        })
        .catch(() => showMsg('获取结果出错'));
};

// 渲染表格函数
function renderTable(data) {
    const resultTable = document.getElementById('result-table');
    resultTable.innerHTML = ''; // 清空表格内容

    if (data.length === 0) {
        resultTable.innerHTML = '<tr><td>无数据</td></tr>';
        return;
    }

    // 创建表头
    const headers = Object.keys(data[0]);
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');
    headers.forEach(header => {
        const th = document.createElement('th');
        th.textContent = header;
        headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);
    resultTable.appendChild(thead);

    // 创建表格内容
    const tbody = document.createElement('tbody');
    data.forEach(row => {
        const tr = document.createElement('tr');
        headers.forEach(header => {
            const td = document.createElement('td');
            td.textContent = row[header];
            tr.appendChild(td);
        });
        tbody.appendChild(tr);
    });
    resultTable.appendChild(tbody);
}

// 下载Excel----------------------------------------------------------------------------
document.getElementById('downloadBtn').onclick = () => {
    window.open('/download', '_blank');
};

//页面关闭时自动清空文件夹-----------------------------------------------------------------
window.addEventListener('beforeunload', () => {
    navigator.sendBeacon('/clear_folders');
});


//按钮状态更新----------------------------------------------------------------------------

apiKeyInput.addEventListener('input', updateButtonStates);
apiHostInput.addEventListener('input', updateButtonStates);
const checkElementsExist = setInterval(() => {
    updateButtonStates();
}, 1000); // 每 1000 毫秒检查一次

function updateButtonStates() {
    const runBtn = document.getElementById('runBtn');
    const resultBtn = document.getElementById('resultBtn');
    const downloadBtn = document.getElementById('downloadBtn');

    const apiKeyInput = document.getElementById('apiKeyInput').value.trim();
    const apiHostInput = document.getElementById('apiHostInput').value.trim();
    const headerInput = document.querySelector('.header-input').value.trim(); // 选择第一个具有 header-input 类的元素
    const fileItem = document.querySelector('.file-item').textContent.trim(); // 选择第一个具有 file-item 类的元素

    if (!apiKeyInput || !apiHostInput || !headerInput || !fileItem) {
        runBtn.classList.add('disabled');
        resultBtn.classList.add('disabled');
        downloadBtn.classList.add('disabled');
        return;
    }else {
        // Enable buttons
        runBtn.classList.remove('disabled');
        resultBtn.classList.remove('disabled');
        downloadBtn.classList.remove('disabled');
    }
    }