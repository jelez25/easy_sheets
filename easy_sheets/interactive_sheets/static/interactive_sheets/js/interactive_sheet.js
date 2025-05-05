document.addEventListener('DOMContentLoaded', function () {
    const imageInput = document.getElementById('id_base_image');
    const uploadedImage = document.getElementById('uploaded-image');
    const interactiveArea = document.getElementById('interactive-area');
    const interactiveForm = document.getElementById('interactive-form');
    const interactiveDataInput = document.getElementById('interactive-options'); // Usar el input oculto existente

    // Ajustar el tamaño de la imagen al cargarla
    imageInput.addEventListener('change', function (event) {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function (e) {
                uploadedImage.src = e.target.result;
                uploadedImage.style.display = 'block';

                // Ajustar el ancho de la imagen al ancho del área interactiva
                uploadedImage.onload = function () {
                    const areaWidth = interactiveArea.offsetWidth;
                    uploadedImage.style.width = `${areaWidth}px`;
                    uploadedImage.style.height = 'auto'; // Mantener la proporción
                };
            };
            reader.readAsDataURL(file);
        } else {
            // Si no hay archivo seleccionado, ocultar la imagen
            uploadedImage.src = '#';
            uploadedImage.style.display = 'none';
        }
    });

    // Manejar el caso de quitar la imagen
    imageInput.addEventListener('input', function () {
        if (!imageInput.value) {
            uploadedImage.src = '#';
            uploadedImage.style.display = 'none';
        }
    });

    // Add interactive elements
    document.getElementById('add-text-box').addEventListener('click', function () {
        addInteractiveElement('Cuadro de Texto');
    });

    document.getElementById('add-union').addEventListener('click', function () {
        addInteractiveElement('Union Point');
    });

    document.getElementById('add-check').addEventListener('click', function () {
        addInteractiveElement('Check');
    });

    document.getElementById('add-select').addEventListener('click', function () {
        addInteractiveElement('Dropdown');
    });

    document.getElementById('add-draggable').addEventListener('click', function () {
        addInteractiveElement('Elemento Arrastrable');
    });

    function addInteractiveElement(type) {
        console.log(`Creando elemento interactivo de tipo: ${type}`); // Log para verificar el tipo de elemento

        // Crear un contenedor para el elemento interactivo
        const container = document.createElement('div');
        container.className = 'interactive-container';
        container.style.position = 'absolute';
        container.style.top = '50px';
        container.style.left = '50px';
        container.style.width = 'fit-content'; // Ajustar al contenido
        container.style.height = 'fit-content';

        let element = null; // Inicializar la variable element

        if (type === 'Cuadro de Texto') {
            // Crear un área de texto
            element = document.createElement('textarea');
            element.className = 'interactive-element';
            element.placeholder = 'Escribe aquí...';
            element.style.resize = 'both'; // Permitir redimensionar
            element.style.width = '150px';
            element.style.height = '50px';
        } else if (type === 'Union Point') {
            // Crear un punto de unión (puede ser un div o cualquier otro elemento)
            element = document.createElement('div');
            element.className = 'union-point';
            element.style.width = '20px';
            element.style.height = '20px';
            element.style.backgroundColor = 'black'; // Color del punto de unión
            element.style.borderRadius = '50%'; // Hacerlo circular
        } else if (type === 'Elemento Arrastrable') {
            // Crear el elemento arrastrable
            console.log('Creando un elemento arrastrable');
            element = document.createElement('div');
            element.className = 'draggable-element';
            element.textContent = 'Elemento Arrastrable';
            element.style.padding = '10px';
            element.style.border = '1px solid black';
            element.style.backgroundColor = 'white';
            element.style.cursor = 'grab';
        } else if (type === 'Check') {
            // Crear un contenedor para el checkbox
            console.log('Creando un checkbox');
            element = document.createElement('div');
            element.className = 'check-container';

            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.id = `checkbox-${Date.now()}`; // ID único para asociar con el label
            checkbox.className = 'interactive-checkbox';

            const label = document.createElement('label');
            label.setAttribute('for', checkbox.id); // Asociar el label al checkbox
            label.className = 'custom-checkbox';

            // Añadir el checkbox y el label al contenedor
            element.appendChild(checkbox);
            element.appendChild(label);
        } else if (type === 'Dropdown') {
            // Crear un contenedor para el dropdown
            console.log('Creando un dropdown');
            element = document.createElement('div');
            element.className = 'dropdown-container';
            element.style.width = 'fit-content'; // Ajustar al contenido
            element.style.height = 'fit-content';

            const select = document.createElement('select');
            select.className = 'interactive-element';

            const option1 = document.createElement('option');
            option1.textContent = 'Opción 1';
            const option2 = document.createElement('option');
            option2.textContent = 'Opción 2';

            select.appendChild(option1);
            select.appendChild(option2);

            element.appendChild(select);

            // Ajustar la altura del contenedor al tamaño del select
            select.addEventListener('change', function () {
                element.style.height = `${select.offsetHeight}px`;
            });

            // Ajustar la altura inicial del contenedor
            container.style.height = `${select.offsetHeight}px`;
        }

        // Verificar que element es un nodo válido antes de añadirlo al contenedor
        if (element) {
            container.appendChild(element);

            // Crear el botón de eliminación
            const deleteButton = document.createElement('button');
            deleteButton.className = 'delete-button';
            deleteButton.textContent = 'X';
            deleteButton.style.position = 'absolute';

            // Ajustar posición del botón de eliminación
            if (type === 'Dropdown') {
                deleteButton.style.top = '-25px'; // Posicionar más arriba
                deleteButton.style.left = '-10px'; // Posicionar ligeramente a la izquierda
            } else {
                deleteButton.style.top = '-10px'; // Posición por defecto
                deleteButton.style.left = '-10px'; // Posición por defecto
            }

            // Evento para eliminar el contenedor completo
            deleteButton.addEventListener('click', function () {
                console.log('Eliminando contenedor interactivo');
                interactiveArea.removeChild(container);
            });

            // Añadir el botón de eliminación al contenedor
            container.appendChild(deleteButton);

            // Crear el botón "Editar" solo para elementos arrastrables y dropdown
            if (type === 'Elemento Arrastrable' || type === 'Dropdown') {
                const editButton = document.createElement('button');
                editButton.type = 'button';
                editButton.className = type === 'Elemento Arrastrable' ? 'edit-draggable' : 'edit-dropdown';
                editButton.innerHTML = '&#9998;'; // Icono de lápiz
                editButton.style.position = 'absolute';

                // Ajustar posición del botón de edición
                if (type === 'Dropdown') {
                    editButton.style.top = '-25px'; // Posicionar más arriba
                    editButton.style.right = '-110px'; // Posicionar más a la derecha
                } else {
                    editButton.style.top = '-10px'; // Posición por defecto
                    editButton.style.right = '-10px'; // Posición por defecto
                }

                // Añadir evento al botón para editar el contenido
                editButton.addEventListener('click', function () {
                    if (type === 'Elemento Arrastrable') {
                        const newText = prompt('Edita el contenido del elemento:', element.textContent);
                        if (newText !== null) {
                            element.textContent = newText;
                        }
                    } else if (type === 'Dropdown') {
                        editDropdownOptions(element.querySelector('select'));
                    }
                });

                // Añadir el botón "Editar" al contenedor
                container.appendChild(editButton);
            }

            // Hacer el contenedor arrastrable
            console.log('Haciendo el contenedor arrastrable');
            makeDraggable(container);

            // Añadir el contenedor al área interactiva
            console.log('Añadiendo contenedor al área interactiva');
            interactiveArea.appendChild(container);
        } else {
            console.error('No se pudo crear el elemento interactivo');
        }
    }

    function editDropdownOptions(selectElement) {
        // Get current options as a comma-separated string
        const options = Array.from(selectElement.options).map(option => option.textContent);
        const newOptions = prompt(
            'Edita las opciones separadas por comas:',
            options.join(', ') // Pre-fill the prompt with current options
        );

        if (newOptions !== null) {
            // Clear existing options
            selectElement.innerHTML = '';
            // Add new options from the user input
            newOptions.split(',').forEach(optionText => {
                const option = document.createElement('option');
                option.textContent = optionText.trim();
                selectElement.appendChild(option);
            });
        }
    }

    

    function makeDraggable(element, onDragCallback) {
        let isDragging = false;
        let offsetX = 0;
        let offsetY = 0;

        element.addEventListener('mousedown', function (e) {
            isDragging = true;
            offsetX = e.clientX - element.getBoundingClientRect().left;
            offsetY = e.clientY - element.getBoundingClientRect().top;
            element.style.cursor = 'grabbing';
        });

        document.addEventListener('mousemove', function (e) {
            if (isDragging) {
                const rect = interactiveArea.getBoundingClientRect();
                const x = e.clientX - rect.left - offsetX;
                const y = e.clientY - rect.top - offsetY;

                // Ensure the element stays within the interactive area
                const maxX = rect.width - element.offsetWidth;
                const maxY = rect.height - element.offsetHeight;

                element.style.left = `${Math.max(0, Math.min(x, maxX))}px`;
                element.style.top = `${Math.max(0, Math.min(y, maxY))}px`;

                if (onDragCallback) {
                    onDragCallback();
                }
            }
        });

        document.addEventListener('mouseup', function () {
            if (isDragging) {
                isDragging = false;
                element.style.cursor = 'grab';
            }
        });
    }

    // Antes de enviar el formulario, recopilar los datos de los elementos interactivos
    interactiveForm.addEventListener('submit', function (e) {
        const interactiveElements = interactiveArea.querySelectorAll('.check-container, .dropdown-container, textarea, .draggable-container, .union-container');
        const interactiveData = [];

        interactiveElements.forEach(element => {
            const rect = element.getBoundingClientRect();
            const parentRect = interactiveArea.getBoundingClientRect();

            // Determinar el tipo de elemento
            let type;
            let content = null;

            if (element.classList.contains('check-container')) {
                type = 'Check';
                const checkbox = element.querySelector('input[type="checkbox"]');
                content = checkbox.checked; // Guardar si el checkbox está marcado o no
            } else if (element.classList.contains('dropdown-container')) {
                type = 'Dropdown';
                const select = element.querySelector('select');
                content = Array.from(select.options).map(option => option.textContent); // Guardar las opciones del dropdown
            } else if (element.tagName === 'TEXTAREA') {
                type = 'Cuadro de Texto';
                content = element.value; // Guardar el contenido del cuadro de texto
            } else if (element.classList.contains('draggable-container')) {
                type = 'Elemento Arrastrable';
                const draggableElement = element.querySelector('.draggable-element');
                content = draggableElement.textContent; // Guardar el texto del elemento arrastrable
            } else if (element.classList.contains('union-container')) {
                type = 'union';
                const line = element.querySelector('.union-line');
                content = {
                    width: line.offsetWidth // Guardar el ancho de la línea de unión
                };
            }

            // Guardar los datos del elemento
            interactiveData.push({
                type: type,
                x: rect.left - parentRect.left,
                y: rect.top - parentRect.top,
                width: rect.width,
                height: rect.height,
                content: content
            });
        });

        // Almacenar los datos como JSON en el input oculto
        interactiveDataInput.value = JSON.stringify(interactiveData);
    });
});