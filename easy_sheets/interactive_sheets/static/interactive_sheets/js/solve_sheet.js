document.addEventListener('DOMContentLoaded', async function () {
    const interactiveArea = document.getElementById('interactive-area');
    const interactiveAreaContainer = document.getElementById('interactive-area-container');
    const uploadedImage = document.getElementById('uploaded-image');
    const sheetId = interactiveArea.dataset.sheetId;
    const submitBtn = document.getElementById('submit-sheet-btn');
    const submitForm = document.getElementById('student-answers-form');
    const studentAnswersInput = document.getElementById('student-answers');
    const submitConfirmModalElement = document.getElementById('submitConfirmModal'); // Obtener el elemento del modal
    const submitConfirmModal = new bootstrap.Modal(submitConfirmModalElement); // Crear instancia de Bootstrap Modal
    const confirmSubmitBtn = document.getElementById('confirm-submit');

    // Conexiones entre puntos
    const connections = [];
    let currentlyConnecting = null;
    
    try {
        // Cargar los datos desde el endpoint
        const response = await fetch(`/sheets/api/sheet/${sheetId}/interactive-options/`);
        if (!response.ok) {
            throw new Error(`Error al cargar los datos interactivos: ${response.statusText}`);
        }
        const interactiveData = await response.json();

        console.log("Datos interactivos cargados:", interactiveData);

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
                    interactiveAreaContainer.style.overflowX = 'auto';
                }
                
                console.log(`Imagen ajustada: ${areaHeight}px alto, ${newWidth}px ancho`);
                
                // Renderizar los elementos interactivos después de ajustar el tamaño
                renderInteractiveElements();
            };
            
            if (!uploadedImage.complete) {
                uploadedImage.src = uploadedImage.src;
            } else {
                const evt = new Event('load');
                uploadedImage.dispatchEvent(evt);
            }
        } else {
            // Si no hay imagen, renderizar los elementos directamente
            renderInteractiveElements();
        }

        // Configurar botón de envío
        if (submitBtn) {
            submitBtn.addEventListener('click', function () {
                // Mostrar modal de confirmación
                submitConfirmModal.show();
            });

            // Confirmar envío
            confirmSubmitBtn.addEventListener('click', function () {
                // Recopilar todas las respuestas
                const answers = collectStudentAnswers();
                
                // Quitar el foco del botón antes de continuar
                confirmSubmitBtn.blur();

                // Cerrar el modal primero
                submitConfirmModal.hide();
                
                // Crear un objeto FormData y añadir los datos
                const formData = new FormData();
                formData.append('csrfmiddlewaretoken', document.querySelector('input[name="csrfmiddlewaretoken"]').value);
                formData.append('student_answers', JSON.stringify(answers));
                
                // Usar fetch en lugar de enviar el formulario directamente
                fetch(submitForm.action, {
                    method: 'POST',
                    body: formData
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`Error del servidor: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    console.log('Respuesta del servidor:', data);
                    
                    if (data.success) {
                        // Redirigir a la URL proporcionada por el servidor
                        window.location.href = data.redirect_url;
                    } else {
                        alert('Error: ' + data.message);
                    }
                })
                .catch(error => {
                    console.error('Error al enviar las respuestas:', error);
                    alert('Error al enviar las respuestas. Por favor, inténtalo de nuevo.');
                });
            });
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

        // Función para recopilar las respuestas de los elementos interactivos
        function collectStudentAnswers() {
            const answers = {};
            let hasAnswers = false;
            
            document.querySelectorAll('.interactive-element').forEach(element => {
                const id = element.dataset.optionId;
                if (id) {
                    hasAnswers = true;
                    if (element.type === 'checkbox') {
                        answers[id] = element.checked;
                    } else if (element.tagName === 'TEXTAREA' || element.tagName === 'INPUT') {
                        answers[id] = element.value;
                    } else if (element.tagName === 'SELECT') {
                        answers[id] = element.value;
                    } else if (element.classList.contains('union-point')) {
                        // Guardar información de los puntos de unión
                        answers[id] = {
                            connectedTo: connections
                                .filter(conn => conn.from === id || conn.to === id)
                                .map(conn => (conn.from === id ? conn.to : conn.from))
                        };
                    } else if (element.classList.contains('draggable-element')) {
                        // Guardar posición de los elementos arrastrables
                        const rect = element.parentElement.getBoundingClientRect();
                        const areaRect = interactiveArea.getBoundingClientRect();
                        answers[id] = {
                            x: rect.left - areaRect.left,
                            y: rect.top - areaRect.top
                        };
                    }
                } else {
                    console.warn('Elemento sin data-option-id:', element);
                }
            });
            
            console.log('Respuestas recopiladas:', answers);
            return answers;
        }
        
    } catch (error) {
        console.error('Error al cargar los datos interactivos:', error);
    }

    function renderCheck(data) {
        const container = document.createElement('div');
        container.className = 'check-container interactive-container';
        container.style.position = 'absolute';
        container.style.top = `${data.y}px`;
        container.style.left = `${data.x}px`;
        container.style.width = `${data.width || 30}px`;
        container.style.height = `${data.height || 30}px`;
        container.style.display = 'flex';
        container.style.alignItems = 'center';
        container.style.justifyContent = 'center';

        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.className = 'interactive-checkbox interactive-element';
        checkbox.checked = data.content || false; // Estado inicial
        checkbox.style.width = '20px';
        checkbox.style.height = '20px';
        checkbox.dataset.optionId = `option-check${Date.now()}`; // Guardar el ID del elemento para la recopilación de respuestas

        // Agregar evento para alternar el estado del checkbox
        container.addEventListener('click', function () {
            checkbox.checked = !checkbox.checked; // Alternar el estado
            console.log(`Checkbox ${checkbox.dataset.optionId} cambiado a: ${checkbox.checked}`);
        });

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
        textBox.style.width = `${data.width || 150}px`;
        textBox.style.height = `${data.height || 75}px`;
        textBox.value = data.content || '';
        textBox.disabled = false; // Permitir interacción
        textBox.dataset.optionId = `option-textbox${Date.now()}`; // Guardar el ID del elemento para la recopilación de respuestas
        
        interactiveArea.appendChild(textBox);
        console.log('TextBox renderizado en:', data.x, data.y);
    }

    function renderDropdown(data) {
        const container = document.createElement('div');
        container.className = 'dropdown-container interactive-container';
        container.style.position = 'absolute';
        container.style.top = `${data.y}px`;
        container.style.left = `${data.x}px`;
        container.style.width = `${data.width || 150}px`;
        container.style.height = `${data.height || 30}px`;

        const select = document.createElement('select');
        select.className = 'interactive-element';
        select.style.width = '100%';
        select.disabled = false; // Permitir interacción
        select.dataset.optionId = `option-dropdown${Date.now()}`; // Guardar el ID del elemento para la recopilación de respuestas
        
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
        container.className = 'draggable-container interactive-container';
        container.style.position = 'absolute';
        container.style.top = `${data.y}px`;
        container.style.left = `${data.x}px`;
        container.style.width = `${data.width || 150}px`;
        container.style.height = `${data.height || 50}px`;
        container.style.border = '1px solid #000';
        container.style.backgroundColor = '#f8f9fa';
        container.style.cursor = 'grab';

        const draggableElement = document.createElement('div');
        draggableElement.className = 'draggable-element interactive-element';
        draggableElement.textContent = data.content || 'Elemento arrastrable';
        draggableElement.style.padding = '5px';
        draggableElement.style.height = '100%';
        draggableElement.style.width = '100%';
        draggableElement.style.display = 'flex';
        draggableElement.style.alignItems = 'center';
        draggableElement.style.justifyContent = 'center';
        draggableElement.dataset.optionId = `option-draggable${Date.now()}`; // Guardar el ID del elemento para la recopilación de respuestas
        
        // Hacer el elemento arrastrable
        makeElementDraggable(container);

        container.appendChild(draggableElement);
        interactiveArea.appendChild(container);
        console.log('Elemento arrastrable renderizado en:', data.x, data.y);
    }

    function renderUnion(data) {
        console.log('Renderizando punto de unión con datos:', data);
        
        const container = document.createElement('div');
        container.className = 'union-container interactive-container';
        container.style.position = 'absolute';
        container.style.top = `${data.y}px`;
        container.style.left = `${data.x}px`;
        
        const point = document.createElement('div');
        point.className = 'union-point interactive-element';
        point.style.width = '15px';
        point.style.height = '15px';
        point.style.borderRadius = '50%';
        point.style.backgroundColor = '#000000';
        point.style.border = '2px solid #000';
        point.style.cursor = 'pointer';
        point.dataset.optionId = `point-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        
        // Permitir crear conexiones entre puntos
        point.addEventListener('click', function(e) {
            handlePointClick(point);
        });
        
        container.appendChild(point);
        interactiveArea.appendChild(container);
        console.log('Punto de unión renderizado en:', data.x, data.y);
    }
    
    function makeElementDraggable(element) {
        let isDragging = false;
        let offsetX = 0;
        let offsetY = 0;

        element.addEventListener('mousedown', function(e) {
            isDragging = true;
            offsetX = e.clientX - element.getBoundingClientRect().left;
            offsetY = e.clientY - element.getBoundingClientRect().top;
            element.style.cursor = 'grabbing';
            e.preventDefault(); // Prevenir selección de texto al arrastrar
        });

        document.addEventListener('mousemove', function(e) {
            if (isDragging) {
                const rect = interactiveArea.getBoundingClientRect();
                const x = e.clientX - rect.left - offsetX;
                const y = e.clientY - rect.top - offsetY;

                const maxX = rect.width - element.offsetWidth;
                const maxY = rect.height - element.offsetHeight;

                element.style.left = `${Math.max(0, Math.min(x, maxX))}px`;
                element.style.top = `${Math.max(0, Math.min(y, maxY))}px`;
                
                // Si hay líneas conectadas a este elemento, actualizar sus posiciones
                updateConnectedLines(element);
            }
        });

        document.addEventListener('mouseup', function() {
            if (isDragging) {
                isDragging = false;
                element.style.cursor = 'grab';
            }
        });
    }
    
    function handlePointClick(point) {
        // Si no hay punto seleccionado, este es el primero
        if (!currentlyConnecting) {
            currentlyConnecting = point;
            point.style.backgroundColor = 'red'; // Cambiar color para indicar selección
            return;
        }
        
        // Si el punto es el mismo, deseleccionar
        if (currentlyConnecting === point) {
            currentlyConnecting.style.backgroundColor = '#000000';
            currentlyConnecting = null;
            return;
        }
        
        // Verificar si alguno de los puntos ya tiene una conexión
        const pointId1 = currentlyConnecting.dataset.optionId;
        const pointId2 = point.dataset.optionId;
        
        if (isPointConnected(pointId1) || isPointConnected(pointId2)) {
            console.log('Conexión no permitida entre:', pointId1, pointId2);
            alert('Cada punto solo puede tener una conexión.');
            
            currentlyConnecting.style.backgroundColor = '#000000';
            currentlyConnecting = null;
            return;
        }
        
        // Crear la conexión
        createConnection(currentlyConnecting, point);
        
        // Resetear selección
        currentlyConnecting.style.backgroundColor = '#000000';
        currentlyConnecting = null;
    }
    
    function isPointConnected(pointId) {
        return connections.some(conn => conn.from === pointId || conn.to === pointId);
    }
    
    function createConnection(point1, point2) {
        const line = document.createElement('div');
        line.className = 'connection-line';
        
        // Obtener posiciones de los puntos
        const p1Rect = point1.getBoundingClientRect();
        const p2Rect = point2.getBoundingClientRect();
        const areaRect = interactiveArea.getBoundingClientRect();
        
        // Calcular posiciones relativas al área interactiva
        const x1 = p1Rect.left + p1Rect.width/2 - areaRect.left;
        const y1 = p1Rect.top + p1Rect.height/2 - areaRect.top;
        const x2 = p2Rect.left + p2Rect.width/2 - areaRect.left;
        const y2 = p2Rect.top + p2Rect.height/2 - areaRect.top;
        
        // Calcular longitud y ángulo de la línea
        const length = Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2));
        const angle = Math.atan2(y2 - y1, x2 - x1) * 180 / Math.PI;
        
        // Estilizar la línea
        line.style.position = 'absolute';
        line.style.left = `${x1}px`;
        line.style.top = `${y1}px`;
        line.style.width = `${length}px`;
        line.style.height = '2px';
        line.style.backgroundColor = 'black';
        line.style.transformOrigin = '0 0';
        line.style.transform = `rotate(${angle}deg)`;
        line.style.zIndex = '5';
        
        // Añadir botón para eliminar la conexión
        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'delete-connection-btn';
        deleteBtn.innerHTML = '&times;';
        deleteBtn.style.position = 'absolute';
        deleteBtn.style.left = `${(x1 + x2) / 2 - 10}px`;
        deleteBtn.style.top = `${(y1 + y2) / 2 - 10}px`;
        deleteBtn.style.zIndex = '6';
        deleteBtn.style.display = 'none';
        deleteBtn.style.width = '20px';
        deleteBtn.style.height = '20px';
        deleteBtn.style.borderRadius = '50%';
        deleteBtn.style.border = '1px solid red';
        deleteBtn.style.backgroundColor = 'white';
        deleteBtn.style.color = 'red';
        deleteBtn.style.cursor = 'pointer';
        
        // Mostrar botón de eliminar al pasar por encima de la línea
        line.addEventListener('mouseover', () => deleteBtn.style.display = 'block');
        line.addEventListener('mouseout', () => deleteBtn.style.display = 'none');
        deleteBtn.addEventListener('mouseover', () => deleteBtn.style.display = 'block');
        deleteBtn.addEventListener('mouseout', () => deleteBtn.style.display = 'none');
        
        // Eliminar la conexión al hacer clic en el botón
        deleteBtn.addEventListener('click', () => {
            interactiveArea.removeChild(line);
            interactiveArea.removeChild(deleteBtn);
            const index = connections.findIndex(c => c.line === line);
            if (index !== -1) {
                connections.splice(index, 1);
            }
        });
        
        // Añadir elementos al DOM
        interactiveArea.appendChild(line);
        interactiveArea.appendChild(deleteBtn);
        
        // Guardar la conexión
        connections.push({
            from: point1.dataset.optionId,
            to: point2.dataset.optionId,
            line: line,
            deleteBtn: deleteBtn
        });
    }
    
    function updateConnectedLines(element) {
        // Buscar todos los puntos dentro del elemento
        const points = element.querySelectorAll('.union-point');
        
        points.forEach(point => {
            const pointId = point.dataset.id;
            
            // Actualizar todas las conexiones que involucran este punto
            connections.forEach(conn => {
                if (conn.from === pointId || conn.to === pointId) {
                    // Recalcular la posición de la línea
                    let point1, point2;
                    
                    // Encontrar los elementos de punto por sus IDs
                    const allPoints = interactiveArea.querySelectorAll('.union-point');
                    allPoints.forEach(p => {
                        if (p.dataset.id === conn.from) point1 = p;
                        if (p.dataset.id === conn.to) point2 = p;
                    });
                    
                    if (point1 && point2) {
                        const p1Rect = point1.getBoundingClientRect();
                        const p2Rect = point2.getBoundingClientRect();
                        const areaRect = interactiveArea.getBoundingClientRect();
                        
                        const x1 = p1Rect.left - areaRect.left;
                        const y1 = p1Rect.top - areaRect.top;
                        const x2 = p2Rect.left - areaRect.left;
                        const y2 = p2Rect.top - areaRect.top;
                        
                        const length = Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2));
                        const angle = Math.atan2(y2 - y1, x2 - x1) * 180 / Math.PI;
                        
                        conn.line.style.left = `${x1}px`;
                        conn.line.style.top = `${y1}px`;
                        conn.line.style.width = `${length}px`;
                        conn.line.style.transform = `rotate(${angle}deg)`;
                        
                        conn.deleteBtn.style.left = `${(x1 + x2) / 2 - 10}px`;
                        conn.deleteBtn.style.top = `${(y1 + y2) / 2 - 10}px`;
                    }
                }
            });
        });
    }
});