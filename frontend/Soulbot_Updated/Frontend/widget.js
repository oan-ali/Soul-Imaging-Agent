(function() {
    const script = document.currentScript;
    const position = script.getAttribute('data-position') || 'bottom-right';
    const color = script.getAttribute('data-color') || '#3B82F6';
    const text = script.getAttribute('data-text') || 'Chat with us';
    const baseUrl = script.src.split('/widget.js')[0];

    // Create Container
    const container = document.createElement('div');
    container.style.position = 'fixed';
    container.style.zIndex = '999999';
    
    if (position.includes('bottom')) container.style.bottom = '20px';
    else container.style.top = '20px';
    
    if (position.includes('right')) container.style.right = '20px';
    else container.style.left = '20px';

    // Create Button
    const button = document.createElement('button');
    button.innerHTML = '💬 ' + text;
    button.style.background = color;
    button.style.color = 'white';
    button.style.border = 'none';
    button.style.padding = '12px 24px';
    button.style.borderRadius = '30px';
    button.style.cursor = 'pointer';
    button.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
    button.style.fontFamily = 'Inter, sans-serif';
    button.style.fontWeight = '600';

    // Create Iframe
    const iframe = document.createElement('iframe');
    iframe.src = baseUrl + '/orb';
    iframe.style.width = '380px';
    iframe.style.height = '600px';
    iframe.style.border = 'none';
    iframe.style.borderRadius = '16px';
    iframe.style.display = 'none';
    iframe.style.boxShadow = '0 12px 40px rgba(0,0,0,0.2)';
    iframe.style.marginTop = '10px';

    button.onclick = function() {
        if (iframe.style.display === 'none') {
            iframe.style.display = 'block';
        } else {
            iframe.style.display = 'none';
        }
    };

    container.appendChild(iframe);
    container.appendChild(button);
    document.body.appendChild(container);

    if (position.includes('top')) {
        container.style.display = 'flex';
        container.style.flexDirection = 'column-reverse';
    }
})();
