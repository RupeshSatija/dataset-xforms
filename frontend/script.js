let originalContent = '';

document.getElementById('fileInput').addEventListener('change', async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('/api/text/upload', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        originalContent = data.content;
        displayTokenizedText(data.tokens, 'originalText');
    } catch (error) {
        console.error('Error uploading file:', error);
    }
});

async function applyTransformation(transformationType) {
    if (!originalContent) return;

    try {
        const response = await fetch('/api/text/transform', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                text: originalContent,
                transformation: transformationType
            })
        });
        const data = await response.json();
        displayTransformedText(data);
    } catch (error) {
        console.error('Error applying transformation:', error);
    }
}

function displayTokenizedText(tokens, elementId) {
    const element = document.getElementById(elementId);
    element.innerHTML = '';
    
    tokens.forEach(token => {
        const span = document.createElement('span');
        span.className = 'token';
        span.textContent = token;
        element.appendChild(span);
    });
}

function displayTransformedText(data) {
    console.log("Transformation data:", data);
    const container = document.getElementById('transformed-text');
    container.innerHTML = '';
    
    data.tokens.forEach((token, index) => {
        const span = document.createElement('span');
        span.textContent = token;
        
        if (data.modifications[index]) {
            console.log(`Coloring token: "${token}" with color: ${data.colors[data.type]}`);
            span.style.backgroundColor = data.colors[data.type];
            span.classList.add('modified');
            span.classList.add(data.type);
            
            // Special handling for punctuation
            if (data.type === 'punctuation') {
                span.style.backgroundColor = '#FFB6C1';  // Light pink
                span.style.padding = '0 2px';
                span.style.margin = '0 1px';
            }
        }
        
        // Add space after each token except punctuation
        if (!/^[,.!?;]$/.test(token)) {
            span.textContent += ' ';
        }
        
        container.appendChild(span);
    });
} 