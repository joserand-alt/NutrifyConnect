const http = require('http');

http.get('http://localhost:8080/index.html', (res) => {
    let data = '';
    res.on('data', chunk => data += chunk);
    res.on('end', () => {
        console.log('HTTP Status:', res.statusCode);
        console.log('Data length:', data.length);
        console.log('Includes p-prog:', data.includes('id="p-prog"'));
        console.log('Includes p-exec:', data.includes('id="p-exec"'));
    });
}).on('error', err => {
    console.error('HTTP error:', err.message);
});
