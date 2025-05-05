document.addEventListener('DOMContentLoaded', async function () {
    const interactiveArea = document.getElementById('interactive-area');
    const interactiveAreaContainer = document.getElementById('interactive-area-container');
    const uploadedImage = document.getElementById('uploaded-image');
    const sheetId = interactiveArea.dataset.sheetId; // Leer el ID de la ficha desde un atributo data-*

    try {
        // Cargar los datos desde el endpoint
        const response = await fetch(`/sheets/api/sheet/${sheetId}/interactive-options/`);
        if (!response.ok) {
            throw new Error(`Error al cargar los datos interactivos: ${response.statusText}`);
        }
        const interactiveData = await response.json();

        console.log(interactiveData); // Verificar la estructura de los datos

        // Ajustar la altura de la imagen al área interactiva
        if (uploadedImage) {
            // Esperar a que la imagen se cargue para obtener sus dimensiones reales
            uploadedImage.onload = function() {
                // Calcular la proporción de la imagen
                const imageRatio = this.naturalWidth / this.naturalHeight;
                
                // Ajustar la altura al área
                const areaHeight = interactiveArea.offsetHeight || 600;
                uploadedImage.style.height = `${areaHeight}px`;
                uploadedImage.style.width = 'auto'; // Mantener la proporción
                
                // Calcular el nuevo ancho basado en la proporción
                const newWidth = areaHeight * imageRatio;
                
                // Ajustar el ancho del área interactiva al ancho calculado de la imagen
                interactiveArea.style.width = `${newWidth}px`;
                
                // Ajustar también el ancho del contenedor para mantenerlo alineado
                if (interactiveAreaContainer) {
                    interactiveAreaContainer.style.width = `${newWidth}px`;
                }
                
                console.log(`Imagen ajustada: ${areaHeight}px alto, ${newWidth}px ancho`);
                
                // Renderizar los elementos interactivos después de ajustar el tamaño
                renderInteractiveElements();
            };
            
            // Establecer la fuente de la imagen si aún no está establecida
            if (!uploadedImage.complete) {
                uploadedImage.src = uploadedImage.src;
            } else {
                // Si la imagen ya está cargada, dispara el evento onload manualmente
                const evt = new Event('load');
                uploadedImage.dispatchEvent(evt);
            }
        } else {
            // Si no hay imagen, renderizar los elementos directamente
            renderInteractiveElements();
        }

        // Función para renderizar los elementos interactivos
        function renderInteractiveElements() {
            interactiveData.forEach(item => {
                if (item.type === 'Check') {
                    renderCheck(item);
                } else if (item.type === 'Cuadro de Texto') {
                    renderTextBox(item);
                } else if (item.type === 'Dropdown') {
                    renderDropdown(item);
                } else if (item.type === 'Elemento Arrastrable') {
                    renderDraggable(item);
                } else if (item.type === 'Union Point') {
                    renderUnion(item);
                }
            });
        }
    } catch (error) {
        console.error('Error al cargar los datos interactivos:', error);
    }

    function renderCheck(data) {
        const container = document.createElement('div');
        container.className = 'check-container';
        container.style.position = 'absolute';
        container.style.top = `${data.y}px`;
        container.style.left = `${data.x}px`;
        container.style.width = `${data.width || 30}px`;  // Añadir ancho mínimo de 30px
        container.style.height = `${data.height || 30}px`;  // Añadir alto mínimo de 30px
        container.style.display = 'flex';
        container.style.alignItems = 'center';
        container.style.justifyContent = 'center';

        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.className = 'interactive-checkbox';
        checkbox.checked = data.content;
        checkbox.style.width = '20px';
        checkbox.style.height = '20px';

        const label = document.createElement('label');
        label.className = 'custom-checkbox';

        container.appendChild(checkbox);
        container.appendChild(label);
        interactiveArea.appendChild(container);
        console.log('Check renderizado en:', data.x, data.y);
    }

    function renderTextBox(data) {
        const textBox = document.createElement('textarea');
        textBox.className = 'interactive-element';
        textBox.style.position = 'absolute';
        textBox.style.top = `${data.y}px`;
        textBox.style.left = `${data.x}px`;
        textBox.style.width = `${data.width || 150}px`;  // Establecer un valor predeterminado si width es 0
        textBox.style.height = `${data.height || 75}px`; // Establecer un valor predeterminado si height es 0
        textBox.value = data.content || ''; // Manejar contenido vacío
        interactiveArea.appendChild(textBox);
        console.log('TextBox renderizado en:', data.x, data.y);
    }

    function renderDropdown(data) {
        const container = document.createElement('div');
        container.className = 'dropdown-container';
        container.style.position = 'absolute';
        container.style.top = `${data.y}px`;
        container.style.left = `${data.x}px`;
        container.style.width = `${data.width || 150}px`;  // Establecer un valor predeterminado si width es 0
        container.style.height = `${data.height || 30}px`; // Establecer un valor predeterminado si height es 0

        const select = document.createElement('select');
        select.className = 'interactive-element';
        select.style.width = '100%';
        
        // Asegurarse de que content sea un array
        const options = Array.isArray(data.content) ? data.content : ['Opción por defecto'];
        
        options.forEach(optionText => {
            const option = document.createElement('option');
            option.textContent = optionText;
            select.appendChild(option);
        });

        container.appendChild(select);
        interactiveArea.appendChild(container);
        console.log('Dropdown renderizado en:', data.x, data.y);
    }

    function renderDraggable(data) {
        const container = document.createElement('div');
        container.className = 'draggable-container';
        container.style.position = 'absolute';
        container.style.top = `${data.y}px`;
        container.style.left = `${data.x}px`;
        container.style.width = `${data.width || 150}px`;  // Valor predeterminado si width es 0
        container.style.height = `${data.height || 50}px`; // Valor predeterminado si height es 0
        container.style.border = '1px solid #000';
        container.style.backgroundColor = '#f8f9fa';

        const draggableElement = document.createElement('div');
        draggableElement.className = 'draggable-element';
        draggableElement.textContent = data.content || 'Elemento arrastrable'; // Texto por defecto
        draggableElement.style.padding = '5px';
        draggableElement.style.height = '100%';
        draggableElement.style.display = 'flex';
        draggableElement.style.alignItems = 'center';
        draggableElement.style.justifyContent = 'center';

        container.appendChild(draggableElement);
        interactiveArea.appendChild(container);
        console.log('Elemento arrastrable renderizado en:', data.x, data.y);
    }

    function renderUnion(data) {
        console.log('Renderizando punto de union con datos:', data);
        
        const container = document.createElement('div');
        container.className = 'union-container';
        container.style.position = 'absolute';
        container.style.top = `${data.y}px`;
        container.style.left = `${data.x}px`;
        
        // Crear solo un punto
        const point = document.createElement('div');
        point.className = 'union-point';
        point.style.width = '15px';
        point.style.height = '15px';
        point.style.borderRadius = '50%';
        point.style.backgroundColor = '#000000';
        point.style.border = '2px solid #000';
        point.style.cursor = 'pointer';
        
        container.appendChild(point);
        interactiveArea.appendChild(container);
        console.log('Punto de unión renderizado en:', data.x, data.y);
    }
});