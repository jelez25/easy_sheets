document.addEventListener('DOMContentLoaded', async function() {
    const interactiveArea = document.getElementById('interactive-area');
    const submissionContent = document.getElementById('submission-content');
    const uploadedImage = document.getElementById('uploaded-image');
    const sheetId = interactiveArea.dataset.sheetId;
    const urlParams = new URLSearchParams(window.location.search);
    const studentId = urlParams.get('student_id');
    let scaleRatio = 1;
    
    try {
        // Cargar todos los datos necesarios para la corrección desde la nueva API
        const response = await fetch(`/sheets/api/sheet/${sheetId}/correction/?student_id=${studentId}`);
        if (!response.ok) {
            throw new Error(`Error al cargar datos: ${response.statusText}`);
        }
        
        const correctionData = await response.json();
        
        // Ahora tienes acceso a:
        // - correctionData.interactive_options (opciones interactivas originales)
        // - correctionData.student_answers (respuestas del estudiante)
        // - correctionData.submission (datos de la entrega)
        // - correctionData.student (información del estudiante)
        
        const interactiveOptions = correctionData.interactive_options;
        const studentAnswers = correctionData.student_answers;

        // IMPORTANTE: Define primero todas las funciones auxiliares
        
        // Función para renderizar un checkbox en modo solo lectura
        function renderReadOnlyCheck(option, id, isChecked) {
            const container = document.createElement('div');
            container.className = 'read-only-check';
            container.style.position = 'absolute';
            container.style.top = `${option.y * scaleRatio}px`;
            container.style.left = `${option.x * scaleRatio}px`;
            
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.checked = isChecked;
            checkbox.disabled = true;
            checkbox.dataset.optionId = id;
            
            container.appendChild(checkbox);
            submissionContent.appendChild(container);
        }
        
        // Función para renderizar un cuadro de texto en modo solo lectura
        function renderReadOnlyTextBox(option, id, content) {
            const textbox = document.createElement('div');
            textbox.className = 'read-only-textbox';
            textbox.style.position = 'absolute';
            textbox.style.top = `${option.y * scaleRatio}px`;
            textbox.style.left = `${option.x * scaleRatio}px`;
            textbox.style.width = `${(option.width || 150) * scaleRatio}px`;
            textbox.style.height = `${(option.height || 75) * scaleRatio}px`;
            textbox.textContent = content;
            textbox.dataset.optionId = id;
            
            submissionContent.appendChild(textbox);
        }
        
        // Función para renderizar un dropdown en modo solo lectura
        function renderReadOnlyDropdown(option, id, selectedOption) {
            const dropdown = document.createElement('div');
            dropdown.className = 'read-only-dropdown';
            dropdown.style.position = 'absolute';
            dropdown.style.top = `${option.y * scaleRatio}px`;
            dropdown.style.left = `${option.x * scaleRatio}px`;
            dropdown.style.width = `${(option.width || 150) * scaleRatio}px`;
            dropdown.style.height = `${(option.height || 30) * scaleRatio}px`;
            dropdown.textContent = selectedOption;
            dropdown.dataset.optionId = id;
            
            submissionContent.appendChild(dropdown);
        }
        
        // Función para renderizar un punto de unión en modo solo lectura
        function renderReadOnlyUnionPoint(option, id) {
            const point = document.createElement('div');
            point.className = 'read-only-union-point';
            point.style.position = 'absolute';
            point.style.top = `${option.y * scaleRatio}px`;
            point.style.left = `${option.x * scaleRatio}px`;
            point.style.width = `${15 * scaleRatio}px`;
            point.style.height = `${15 * scaleRatio}px`;
            point.dataset.pointId = id;
            
            submissionContent.appendChild(point);
            return point;
        }
        
        // Función para dibujar una conexión entre dos puntos
        function drawConnection(point1, point2) {
            // Obtener posiciones
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
            
            // Crear la línea
            const line = document.createElement('div');
            line.className = 'connection-line';
            line.style.position = 'absolute';
            line.style.left = `${x1}px`;
            line.style.top = `${y1}px`;
            line.style.width = `${length}px`;
            line.style.height = `${2 * scaleRatio}px`;
            line.style.backgroundColor = 'black';
            line.style.transformOrigin = '0 0';
            line.style.transform = `rotate(${angle}deg)`;
            line.style.zIndex = '5';
            
            submissionContent.appendChild(line);
        }
        
        // Función para dibujar todas las conexiones entre puntos
        function drawConnections(answers) {
            // Obtener todos los puntos de unión con sus conexiones
            const pointConnections = {};
            
            // Recopilar todas las conexiones de los puntos
            for (const [key, value] of Object.entries(answers)) {
                if (key.startsWith('point-') && value && value.connectedTo) {
                    pointConnections[key] = value.connectedTo;
                }
            }
            
            // Para cada punto, dibujar sus conexiones
            for (const [pointId, connectedPoints] of Object.entries(pointConnections)) {
                // Obtener el elemento del punto actual
                const point1 = document.querySelector(`[data-point-id="${pointId}"]`);
                if (!point1) continue;
                
                // Para cada punto conectado, dibujar la línea
                connectedPoints.forEach(connectedId => {
                    const point2 = document.querySelector(`[data-point-id="${connectedId}"]`);
                    if (!point2) return;
                    
                    drawConnection(point1, point2);
                });
            }
        }
        
        // Renderizar elementos interactivos originales con las respuestas sobrepuestas
        function renderInteractiveElements(options, answers) {
            // Mapeo de tipos en español a claves en el JSON
            const typeMapping = {
                'Cuadro de Texto': 'textbox',
                'Dropdown': 'dropdown',
                'Check': 'check',
                'Elemento Arrastrable': 'draggable',
                'Union Point': 'point'
            };
            
            // Extraer el timestamp de una de las claves de respuestas
            const answerKeys = Object.keys(answers);
            const textboxKey = answerKeys.find(key => key.startsWith('option-textbox'));
            const timestamp = textboxKey ? textboxKey.replace('option-textbox', '') : '1746635489144';
            
            // Procesar cada opción interactiva
            options.forEach((item, index) => {
                // Usar el mapping para generar IDs consistentes con el JSON
                const typeKey = typeMapping[item.type] || item.type.toLowerCase().replace(/\s+/g, '-');
                const baseId = `option-${typeKey}${timestamp}`;
                
                if (item.type === 'Cuadro de Texto') {
                    // El valor debe estar en option-textbox* en lugar de option-cuadro-de-texto*
                    const textValue = answers[baseId];
                    renderReadOnlyTextBox(item, baseId, textValue || '');
                } else if (item.type === 'Check') {
                    renderReadOnlyCheck(item, baseId, answers[baseId] === true);
                } else if (item.type === 'Dropdown') {
                    const dropdownValue = answers[baseId] || (item.content ? item.content[0] : 'No seleccionado');
                    renderReadOnlyDropdown(item, baseId, dropdownValue);
                } else if (item.type === 'Union Point') {
                    // Para puntos de unión, usar los IDs exactos del JSON
                    const pointKeys = Object.keys(answers).filter(key => key.startsWith('point-'));
                    const pointId = pointKeys[index] || `point-${timestamp}-${Math.random().toString(36).substr(2, 9)}`;
                    renderReadOnlyUnionPoint(item, pointId);
                }
            });
        }

        function renderStudentResponses(answers) {
            // Mostrar elementos arrastrables primero
            for (const [key, value] of Object.entries(answers)) {
                if (key.startsWith('option-draggable') && value && typeof value === 'object' && 'x' in value && 'y' in value) {
                    // Crear un nuevo elemento arrastrable con las coordenadas de la respuesta
                    const newDraggable = document.createElement('div');
                    newDraggable.className = 'read-only-draggable';
                    newDraggable.style.position = 'absolute';
                    newDraggable.style.left = `${value.x * scaleRatio}px`;
                    newDraggable.style.top = `${value.y * scaleRatio}px`;
                    newDraggable.style.width = `${150 * scaleRatio}px`;
                    newDraggable.style.height = `${50 * scaleRatio}px`;
                    newDraggable.textContent = 'Elemento arrastrable';
                    newDraggable.dataset.optionId = key;
                    submissionContent.appendChild(newDraggable);
                }
            }
            
            // Dibujar conexiones entre puntos
            drawConnections(answers);
        }
        
        // Reemplazar la sección actual del manejo de la imagen con este código
        if (uploadedImage) {
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
                const interactiveAreaContainer = document.getElementById('interactive-area-container');
                if (interactiveAreaContainer) {
                    interactiveAreaContainer.style.width = `${newWidth}px`;
                    interactiveAreaContainer.style.overflowX = 'auto';
                }
                
                console.log(`Imagen ajustada: ${areaHeight}px alto, ${newWidth}px ancho`);
                
                // Calcular la escala para los elementos interactivos
                scaleRatio = 1; // Con este método no necesitamos escalar
                
                // Renderizar los elementos después de ajustar el tamaño
                renderInteractiveElements(interactiveOptions, studentAnswers);
                renderStudentResponses(studentAnswers);
            };
            
            if (!uploadedImage.complete) {
                uploadedImage.src = uploadedImage.src; // Forzar la carga
            } else {
                uploadedImage.dispatchEvent(new Event('load')); // Disparar evento de carga manualmente
            }
        } else {
            // Si no hay imagen, usar dimensiones estándar
            interactiveArea.style.height = '600px';
            interactiveArea.style.width = '800px';
            scaleRatio = 1;
            renderInteractiveElements(interactiveOptions, studentAnswers);
            renderStudentResponses(studentAnswers);
        }
        
    } catch (error) {
        console.error('Error cargando datos para corrección:', error);
        submissionContent.innerHTML = `<div class="alert alert-danger">Error: ${error.message}</div>`;
    }
});