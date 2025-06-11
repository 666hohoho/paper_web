document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('uploadBtn').onclick = uploadFile;
    document.getElementById('runBtn').onclick = runMulti;
    document.getElementById('resultBtn').onclick = getResult;
    document.getElementById('downloadBtn').onclick = downloadExcel;
});

function uploadFile() {
    const fileInput = document.getElementById('fileInput');
    if (!fileInput.files.length) {
        showMsg('请先选择文件');
        return;
    }
    const formData = new FormData();
    for (let i = 0; i < fileInput.files.length; i++) {
        formData.append('files', fileInput.files[i]);
    }
    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) showMsg('上传失败: ' + data.error);
        else if (data.filenames) showMsg('上传成功: ' + data.filenames.join(', '));
        else showMsg('上传成功');
    })
    .catch(() => showMsg('上传出错'));
}

function runMulti() {
    const headersStr = document.getElementById('headersInput').value.trim();
    if (!headersStr) {
        showMsg('请填写表头');
        return;
    }
    const headers = headersStr.split(',').map(h => h.trim()).filter(h => h);
    fetch('/generate_excel', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ headers })
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) showMsg('运行失败: ' + data.error);
        else showMsg('处理完成');
    })
    .catch(() => showMsg('运行出错'));
}

function getResult() {
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
}

function downloadExcel() {
    window.open('/download', '_blank');
}

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