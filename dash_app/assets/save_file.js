window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        large_params_function: function saveTextAsFile(textToWrite)
		{
			var textFileAsBlob = new Blob([textToWrite], {type:'text/plain'}); 
			var downloadLink = document.createElement("a");
			downloadLink.download = "config.yaml";
			downloadLink.innerHTML = "Download File";
			if (window.webkitURL != null)
			{
				// Chrome allows the link to be clicked
				// without actually adding it to the DOM.
				downloadLink.href = window.webkitURL.createObjectURL(textFileAsBlob);
			}
			else
			{
				// Firefox requires the link to be added to the DOM
				// before it can be clicked.
				downloadLink.href = window.URL.createObjectURL(textFileAsBlob);
				downloadLink.onclick = destroyClickedElement;
				downloadLink.style.display = "none";
				document.body.appendChild(downloadLink);
			}
		
			downloadLink.click();
		}
    }
});
