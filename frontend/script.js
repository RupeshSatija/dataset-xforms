let originalContent = '';
let originalImage = null;

document.addEventListener('DOMContentLoaded', () => {
    // Text file input handler
    document.getElementById('textFileInput').addEventListener('change', async (event) => {
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
            document.getElementById('rawText').textContent = originalContent;
        } catch (error) {
            console.error('Error uploading file:', error);
        }
    });

    // Image file input handler
    document.getElementById('imageFileInput').addEventListener('change', async (event) => {
        const file = event.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/api/image/upload', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            originalImage = data.content;
            document.getElementById('originalImage').src = originalImage;
        } catch (error) {
            console.error('Error uploading image:', error);
        }
    });

    // Tokenize button handler
    document.getElementById('tokenizeButton').addEventListener('click', async () => {
        if (!originalContent) return;

        try {
            const response = await fetch('/api/text/tokenize', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    text: originalContent
                })
            });
            const data = await response.json();
            displayTokenizedText(data, 'tokenizedText');
        } catch (error) {
            console.error('Error tokenizing text:', error);
        }
    });
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

function displayTokenizedText(data, elementId) {
    const element = document.getElementById(elementId);
    element.innerHTML = '';
    
    const container = document.createElement('div');
    container.className = 'tokens-container';
    container.style.cursor = 'pointer';
    
    // Handle both chunked and non-chunked responses
    const tokens = data.chunks ? data.chunks[0].tokens : data.tokens;
    const tokenIds = data.chunks ? data.chunks[0].token_ids : null;
    
    container.dataset.state = 'tokenized';
    container.dataset.tokens = JSON.stringify(tokens);
    if (tokenIds) {
        container.dataset.tokenIds = JSON.stringify(tokenIds);
    }
    
    tokens.forEach((token, index) => {
        const span = document.createElement('span');
        span.className = 'token';
        span.textContent = token;
        if (tokenIds) {
            span.title = `ID: ${tokenIds[index]}`;
        }
        
        container.appendChild(span);
        
        // Add space after each token except punctuation
        if (!/^[,.!?;]$/.test(token)) {
            container.appendChild(document.createTextNode(' '));
        }
    });
    
    container.addEventListener('click', async () => {
        const currentState = container.dataset.state;
        const storedTokens = JSON.parse(container.dataset.tokens);
        
        try {
            if (currentState === 'tokenized') {
                if (!container.dataset.tokenIds) {
                    const response = await fetch('/api/text/detokenize', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            tokens: storedTokens
                        })
                    });
                    const data = await response.json();
                    container.dataset.tokenIds = JSON.stringify(data.token_ids);
                }
                
                const tokenIds = JSON.parse(container.dataset.tokenIds);
                container.innerHTML = '';
                tokenIds.forEach((id, index) => {
                    const span = document.createElement('span');
                    span.className = 'token-id';
                    span.textContent = id;
                    span.title = `Token: ${storedTokens[index]}`;
                    container.appendChild(span);
                    
                    if (!/^[,.!?;]$/.test(storedTokens[index])) {
                        container.appendChild(document.createTextNode(' '));
                    }
                });
                container.dataset.state = 'ids';
            } else {
                container.innerHTML = '';
                const tokenIds = JSON.parse(container.dataset.tokenIds);
                storedTokens.forEach((token, index) => {
                    const span = document.createElement('span');
                    span.className = 'token';
                    span.textContent = token;
                    span.title = `ID: ${tokenIds[index]}`;
                    container.appendChild(span);
                    
                    if (!/^[,.!?;]$/.test(token)) {
                        container.appendChild(document.createTextNode(' '));
                    }
                });
                container.dataset.state = 'tokenized';
            }
        } catch (error) {
            console.error('Error toggling token display:', error);
        }
    });
    
    element.appendChild(container);
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

function switchTab(tabName) {
    document.querySelectorAll('.tab-button').forEach(button => {
        button.classList.remove('active');
    });
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    
    document.querySelector(`button[onclick="switchTab('${tabName}')"]`).classList.add('active');
    document.getElementById(`${tabName}-section`).classList.add('active');
}

async function applyImageTransformation(transformationType) {
    if (!originalImage) return;

    try {
        const formData = new FormData();
        const response = await fetch(`/api/image/transform?transformation=${transformationType}`, {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        document.getElementById('transformedImage').src = data.transformed;
    } catch (error) {
        console.error('Error applying image transformation:', error);
    }
} 