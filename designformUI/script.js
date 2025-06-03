console.log("script.js loaded");

document.addEventListener('DOMContentLoaded', function() {
    // --- User Info Population ---
    const submitterNameDisplay = document.getElementById('submitterNameDisplay');
    const submitterIdInput = document.getElementById('submitter_id');
    
    const urlParamsOnLoad = new URLSearchParams(window.location.search);
    const userIdOnLoad = urlParamsOnLoad.get('userId');
    const userNameOnLoad = urlParamsOnLoad.get('userName');

    if (submitterIdInput && userIdOnLoad) {
        submitterIdInput.value = userIdOnLoad;
    }

    if (submitterNameDisplay) {
        if (userNameOnLoad) {
            submitterNameDisplay.value = userNameOnLoad;
        } else if (userIdOnLoad) {
            submitterNameDisplay.value = userIdOnLoad; // Fallback to userId if userName is not provided
        } else {
            submitterNameDisplay.value = '未知用戶';
        }
    }

    // --- Existing Date Logic ---
    const colorDraftDateInput = document.querySelector('input[name="colorDraftDate"]');
    const printDateInput = document.querySelector('input[name="printDate"]');
    if (colorDraftDateInput && printDateInput) {
        const today = new Date();
        const tomorrow = new Date(today);
        tomorrow.setDate(tomorrow.getDate() + 1);
        const year = tomorrow.getFullYear();
        const month = String(tomorrow.getMonth() + 1).padStart(2, '0');
        const day = String(tomorrow.getDate()).padStart(2, '0');
        const minDate = `${year}-${month}-${day}`;
        colorDraftDateInput.setAttribute('min', minDate);
        printDateInput.setAttribute('min', minDate);
        colorDraftDateInput.addEventListener('change', function() {
            if (this.value) {
                printDateInput.setAttribute('min', this.value);
                if (printDateInput.value && printDateInput.value < this.value) {
                    printDateInput.value = '';
                }
            } else {
                printDateInput.setAttribute('min', minDate);
            }
        });
        printDateInput.addEventListener('click', function(event) {
            if (!colorDraftDateInput.value) {
                alert("請先填寫色稿時間");
                event.preventDefault();
                this.blur();
            }
        });
    }

    // --- Existing Specs Logic ---
    const typeSelect = document.querySelector('select[name="type"]');
    const specsDropdownContainer = document.getElementById('specsDropdownContainer');
    const specsSelect = document.getElementById('specsSelect');
    const customSpecsInput = document.getElementById('customSpecsInput');
    const specsCheckboxWrapper = document.getElementById('specsCheckboxWrapper');
    const specsCheckboxContainer = document.getElementById('specsCheckboxContainer');
    const digitalSizes = {
        "800x600px": "800x600 像素 (通用)", "1200x628px": "1200x628 像素 (FB 推薦)",
        "1080x1080px": "1080x1080 像素 (方形/IG)", "1080x1920px": "1080x1920 像素 (限時動態)",
        "820x312px": "820x312 像素 (FB 封面)"
    };
    const paperSizes = { "A4 (21x29.7cm)": "A4 (21x29.7cm)", "21x28cm": "21x28cm" };

    function updateSpecsField(selectedType) {
        specsCheckboxContainer.innerHTML = '';
        specsCheckboxWrapper.style.display = 'none';
        specsDropdownContainer.style.display = 'none';
        customSpecsInput.style.display = 'none';
        if (selectedType === '數位') {
            specsCheckboxWrapper.style.display = 'block';
            for (const value in digitalSizes) {
                const checkboxId = `spec-${value.replace(/[^a-zA-Z0-9]/g, '')}`;
                const div = document.createElement('div');
                div.classList.add('checkbox-option');
                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox'; checkbox.name = 'digitalSpecs[]'; checkbox.value = value; checkbox.id = checkboxId;
                const label = document.createElement('label');
                label.htmlFor = checkboxId; label.textContent = digitalSizes[value];
                div.appendChild(checkbox); div.appendChild(label);
                specsCheckboxContainer.appendChild(div);
            }
        } else if (selectedType === '期刊' || selectedType === '一次刊') {
            specsDropdownContainer.style.display = 'block';
            while (specsSelect.options.length > 2) { specsSelect.remove(1); }
            let customOptionExists = Array.from(specsSelect.options).some(opt => opt.value === 'custom');
            if (!customOptionExists) {
                const customOpt = document.createElement('option'); customOpt.value = "custom"; customOpt.textContent = "自訂";
                specsSelect.appendChild(customOpt);
            }
            const customOption = specsSelect.querySelector('option[value="custom"]');
            for (const value in paperSizes) {
                const option = document.createElement('option'); option.value = value; option.textContent = paperSizes[value];
                if (customOption) { specsSelect.insertBefore(option, customOption); } else { specsSelect.appendChild(option); }
            }
            specsSelect.value = "";
            if (specsSelect.value === 'custom') { customSpecsInput.style.display = 'block'; }
        } else {
            specsDropdownContainer.style.display = 'block';
            while (specsSelect.options.length > 2) { specsSelect.remove(1); }
            specsSelect.value = "";
        }
    }
    if (typeSelect && specsSelect && customSpecsInput && specsCheckboxWrapper && specsCheckboxContainer && specsDropdownContainer) {
        typeSelect.addEventListener('change', function() { updateSpecsField(this.value); });
        specsSelect.addEventListener('change', function() {
            if (this.value === 'custom') { customSpecsInput.style.display = 'block'; customSpecsInput.focus(); } 
            else { customSpecsInput.style.display = 'none'; customSpecsInput.value = ''; }
        });
        updateSpecsField(typeSelect.value);
    }

    // --- Form Submission Logic ---
    const projectForm = document.getElementById('projectForm');
    if (projectForm) {
        projectForm.addEventListener('submit', function(event) {
            event.preventDefault();
            console.log('Form submitted');
            
            // Re-populate hidden fields just before creating FormData, to be absolutely sure
            const currentUrlParams = new URLSearchParams(window.location.search);
            const currentUserId = currentUrlParams.get('userId');
            const currentUserName = currentUrlParams.get('userName');

            if (submitterIdInput && currentUserId) {
                submitterIdInput.value = currentUserId;
            }
            if (submitterNameDisplay) { // submitterNameDisplay is the readonly input
                if (currentUserName) {
                    submitterNameDisplay.value = currentUserName;
                } else if (currentUserId) {
                    submitterNameDisplay.value = currentUserId;
                } else {
                    submitterNameDisplay.value = '未知用戶';
                }
            }
            
            const timestampVal = new Date();
            const gmt8Timestamp = new Intl.DateTimeFormat('sv-SE', {
                timeZone: 'Asia/Taipei', year: 'numeric', month: '2-digit', day: '2-digit',
                hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false
            }).format(timestampVal).replace(' ', 'T') + '+08:00';
            
            const timestampHiddenInput = document.getElementById('timestamp');
            if (timestampHiddenInput) {
                timestampHiddenInput.value = gmt8Timestamp;
            }


            const formData = new FormData(projectForm);
            const selectedType = formData.get('type');
            const dataToSend = {};
            const digitalSpecsArray = [];

            for (let [key, value] of formData.entries()) {
                if (key === 'digitalSpecs[]') {
                    digitalSpecsArray.push(value);
                } else if (key === 'specs' && value === 'custom' && (selectedType === '期刊' || selectedType === '一次刊')) {
                    dataToSend[key] = formData.get('customSpecs') || "未填寫自訂尺寸";
                } else if (key !== 'customSpecs') { 
                    dataToSend[key] = value;
                }
            }

            if (selectedType === '數位' && digitalSpecsArray.length > 0) {
                dataToSend['specs'] = digitalSpecsArray.join(', ');
            } else if (selectedType === '數位' && digitalSpecsArray.length === 0) {
                dataToSend['specs'] = "未選擇任何數位尺寸";
            }
            delete dataToSend['digitalSpecs[]'];
            
            // timestamp and submitter_id should be included via FormData as their hidden inputs are populated
            // submitter_name is also included via FormData from the readonly input

            console.log("--- Data to send to n8n ---", dataToSend);

            fetch('https://bwe.app.n8n.cloud/webhook-test/3dd8e0e0-b591-40d9-8ad9-d037cd750c32', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(dataToSend),
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => {
                        throw new Error(`HTTP error! status: ${response.status}, message: ${err.message || 'Unknown error'}`);
                    });
                }
                return response.json();
            })
            .then(data => {
                console.log('Success:', data);
                alert('表單已成功提交到 n8n！');
                projectForm.reset(); 
                if (typeSelect) { updateSpecsField(typeSelect.value); }
                // Re-populate user info after reset
                if (submitterIdInput && userIdOnLoad) submitterIdInput.value = userIdOnLoad;
                if (submitterNameDisplay) {
                    if (userNameOnLoad) submitterNameDisplay.value = userNameOnLoad;
                    else if (userIdOnLoad) submitterNameDisplay.value = userIdOnLoad;
                    else submitterNameDisplay.value = '未知用戶';
                }
            })
            .catch((error) => {
                console.error('Error:', error);
                alert(`提交到 n8n 失敗: ${error.message}`);
            });
        });
    }
});
