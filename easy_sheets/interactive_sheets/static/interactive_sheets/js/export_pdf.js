document.getElementById('export-pdf').addEventListener('click', function () {
    const area = document.getElementById('interactive-area');
    // Leer los atributos del área interactiva
    const sheetSubject = area.getAttribute('data-subject') || '';
    const sheetStatement = area.getAttribute('data-statement') || '';
    html2canvas(area).then(canvas => {
        const imgData = canvas.toDataURL('image/png');
        // Tamaño A4 en px a 96dpi: 794 x 1123 aprox
        const a4Width = 794;
        const a4Height = 1123;
        const marginX = 40;
        const marginY = 80;
        const contentWidth = a4Width - 2 * marginX;
        const contentHeight = a4Height - marginY - 40; // margen superior para título
        // Escalado proporcional
        let drawWidth = contentWidth;
        let drawHeight = canvas.height * (contentWidth / canvas.width);
        if (drawHeight > contentHeight) {
            drawHeight = contentHeight;
            drawWidth = canvas.width * (contentHeight / canvas.height);
        }
        const offsetX = (a4Width - drawWidth) / 2;
        const offsetY = marginY;
        const pdf = new window.jspdf.jsPDF({
            orientation: 'portrait',
            unit: 'px',
            format: [a4Width, a4Height]
        });
        let currentY = 60;
        // Nombre
        pdf.setFontSize(14);
        pdf.text('Nombre:', marginX, currentY);
        pdf.setLineWidth(0.5);
        // Línea para nombre (más corta, empieza tras un espacio y termina en el mismo punto que la de apellidos)
        const labelSpace = 55; // espacio tras el label
        const nombreLineStart = marginX + labelSpace ;
        const nombreLineEnd = marginX + 220;
        pdf.line(nombreLineStart, currentY + 2, nombreLineEnd, currentY + 2);
        currentY += 30;
        // Apellidos (justo debajo de la línea de nombre, misma terminación, empieza tras un espacio)
        pdf.setFontSize(14);
        pdf.text('Apellidos:', marginX, currentY);
        const apellidosLineStart = marginX + labelSpace ;
        const apellidosLineEnd = nombreLineEnd;
        pdf.line(apellidosLineStart, currentY + 2, apellidosLineEnd, currentY + 2);
        currentY += 40;
        // Asignatura (margen izquierdo, con label)
        pdf.setFontSize(15);
        pdf.text('Asignatura: ' + sheetSubject, marginX, currentY);
        currentY += 30;
        // Enunciado de la ficha (margen izquierdo, debajo de asignatura)
        pdf.setFontSize(15);
        pdf.text(sheetStatement, marginX, currentY);
        currentY += 10;
        // Imagen centrada, ocupando el máximo ancho y alto permitido por los márgenes DIN A4
        let imgDrawWidth = contentWidth;
        let imgDrawHeight = canvas.height * (contentWidth / canvas.width);
        if (imgDrawHeight > contentHeight) {
            imgDrawHeight = contentHeight;
            imgDrawWidth = canvas.width * (contentHeight / canvas.height);
        }
        const imgOffsetX = (a4Width - imgDrawWidth) / 2;
        const imgOffsetY = currentY + 20;
        pdf.addImage(imgData, 'PNG', imgOffsetX, imgOffsetY, imgDrawWidth, imgDrawHeight);
        // Nombre del PDF dinámico
        let cleanSubject = sheetSubject.replace(/[^a-zA-Z0-9_\-]/g, '_').toLowerCase();
        let pdfName = 'sheet_' + cleanSubject + '.pdf';
        pdf.save(pdfName);
    });
});