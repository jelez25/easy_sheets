document.addEventListener('DOMContentLoaded', async function () {
    const interactiveArea = document.getElementById('interactive-area');
    const uploadedImage = document.getElementById('uploaded-image');
    const sheetId = interactiveArea.dataset.sheetId; // Leer el ID de la ficha desde un atributo data-*

    try {
        // Cargar los datos desde el endpoint
        const response = await fetch(`/sheets/api/sheet/${sheetId}/interactive-options/`);
        if (!response.ok) {
            throw new Error(`Error al cargar los datos interactivos: ${response.statusText}`);
        }
        const interactiveData = await response.json();

        // Ajustar la altura de la imagen al área interactiva
        if (uploadedImage) {
            const areaHeight = interactiveArea.offsetHeight;
            uploadedImage.style.height = `${areaHeight}px`;
            uploadedImage.style.width = 'auto'; // Mantener la proporción
        }

        // Renderizar los elementos interactivos
        interactiveData.forEach(item => {
            if (item.type === 'Check') {
                renderCheck(item);
            } else if (item.type === 'Cuadro de Texto') {
                renderTextBox(item);
            } else if (item.type === 'Dropdown') {
                renderDropdown(item);
            } else if (item.type === 'Elemento Arrastrable') {
                renderDraggable(item);
            } else if (item.type === 'union') {
                renderUnion(item);
            }
        });
    } catch (error) {
        console.error('Error al cargar los datos interactivos:', error);
    }

    function renderCheck(data) {
        const container = document.createElement('div');
        container.className = 'check-container';
        container.style.top = `${data.y}px`;
        container.style.left = `${data.x}px`;
        container.style.width = `${data.width}px`;
        container.style.height = `${data.height}px`;

        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.className = 'interactive-checkbox';
        checkbox.checked = data.content;

        const label = document.createElement('label');
        label.className = 'custom-checkbox';

        container.appendChild(checkbox);
        container.appendChild(label);
        interactiveArea.appendChild(container);
    }

    function renderTextBox(data) {
        const textBox = document.createElement('textarea');
        textBox.className = 'interactive-element';
        textBox.style.top = `${data.y}px`;
        textBox.style.left = `${data.x}px`;
        textBox.style.width = `${data.width}px`;
        textBox.style.height = `${data.height}px`;
        textBox.value = data.content; // Establecer el contenido del cuadro de texto
        interactiveArea.appendChild(textBox);
    }

    function renderDropdown(data) {
        const container = document.createElement('div');
        container.className = 'dropdown-container';
        container.style.top = `${data.y}px`;
        container.style.left = `${data.x}px`;
        container.style.width = `${data.width}px`;
        container.style.height = `${data.height}px`;

        const select = document.createElement('select');
        select.className = 'interactive-element';
        data.content.forEach(optionText => {
            const option = document.createElement('option');
            option.textContent = optionText;
            select.appendChild(option);
        });

        container.appendChild(select);
        interactiveArea.appendChild(container);
    }

    function renderDraggable(data) {
        const container = document.createElement('div');
        container.className = 'draggable-container';
        container.style.top = `${data.y}px`;
        container.style.left = `${data.x}px`;
        container.style.width = `${data.width}px`;
        container.style.height = `${data.height}px`;

        const draggableElement = document.createElement('div');
        draggableElement.className = 'draggable-element';
        draggableElement.textContent = data.content; // Establecer el contenido del elemento arrastrable

        container.appendChild(draggableElement);
        interactiveArea.appendChild(container);
    }

    function renderUnion(data) {
        const container = document.createElement('div');
        container.className = 'union-container';
        container.style.top = `${data.y}px`;
        container.style.left = `${data.x}px`;

        const point1 = document.createElement('div');
        point1.className = 'union-point';

        const line = document.createElement('div');
        line.className = 'union-line';
        line.style.width = `${data.width - 40}px`; // Ajustar el ancho para los puntos

        const point2 = document.createElement('div');
        point2.className = 'union-point';

        container.appendChild(point1);
        container.appendChild(line);
        container.appendChild(point2);

        interactiveArea.appendChild(container);
    }
});