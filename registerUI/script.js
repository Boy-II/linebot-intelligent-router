document.addEventListener('DOMContentLoaded', function() {
    console.log("註冊表單腳本已載入");

    // 獲取表單元素
    const registerForm = document.getElementById('registerForm');
    const lineIdInput = document.getElementById('line_id');
    const timestampInput = document.getElementById('timestamp');
    const nameInput = document.querySelector('input[name="name"]');
    const emailPrefixInput = document.querySelector('input[name="email_prefix"]');
    const fullEmailInput = document.getElementById('full_email');
    const mobileInput = document.querySelector('input[name="mobile"]');
    const extensionInput = document.querySelector('input[name="extension"]');

    // 從 URL 參數中獲取 LINE ID
    const urlParams = new URLSearchParams(window.location.search);
    const lineId = urlParams.get('userId');

    // 如果有 LINE ID，則設置到隱藏輸入框中
    if (lineId && lineIdInput) {
        lineIdInput.value = lineId;
    }

    // 處理姓名輸入，限制中文字元最大為 5 個
    if (nameInput) {
        nameInput.addEventListener('input', function() {
            // 計算中文字元數量
            const chineseChars = this.value.match(/[\u4e00-\u9fa5]/g) || [];
            const chineseCount = chineseChars.length;
            
            // 如果中文字元超過 5 個，截斷輸入值
            if (chineseCount > 5) {
                // 找出前 5 個中文字元的位置
                let count = 0;
                let cutIndex = this.value.length;
                
                for (let i = 0; i < this.value.length; i++) {
                    if (/[\u4e00-\u9fa5]/.test(this.value[i])) {
                        count++;
                        if (count > 5) {
                            cutIndex = i;
                            break;
                        }
                    }
                }
                
                this.value = this.value.substring(0, cutIndex);
            }
        });
    }

    // 處理電子郵件輸入
    if (emailPrefixInput && fullEmailInput) {
        emailPrefixInput.addEventListener('input', function() {
            fullEmailInput.value = this.value + '@bwnet.com.tw';
        });
    }

    // 處理行動電話格式
    if (mobileInput) {
        mobileInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, ''); // 移除非數字字符
            
            // 只限制總長度為 10 位數字，不自動添加 09 開頭
            value = value.substr(0, 10);
            
            e.target.value = value;
        });
    }

    // 處理分機號碼格式
    if (extensionInput) {
        extensionInput.addEventListener('input', function(e) {
            let value = e.target.value;
            
            // 確保以 # 開頭
            if (value && !value.startsWith('#')) {
                value = '#' + value;
            }
            
            // 限制只能輸入數字（除了開頭的 #）
            value = value.replace(/[^#0-9]/g, '');
            
            // 限制長度為 # 加上 3-4 位數字
            if (value.length > 5) {
                value = value.substr(0, 5);
            }
            
            e.target.value = value;
        });
    }

    // 處理表單提交
    if (registerForm) {
        registerForm.addEventListener('submit', function(event) {
            event.preventDefault();
            console.log('註冊表單已提交');

            // 設置時間戳
            const timestampVal = new Date();
            const gmt8Timestamp = new Intl.DateTimeFormat('sv-SE', {
                timeZone: 'Asia/Taipei', year: 'numeric', month: '2-digit', day: '2-digit',
                hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false
            }).format(timestampVal).replace(' ', 'T') + '+08:00';
            
            if (timestampInput) {
                timestampInput.value = gmt8Timestamp;
            }

            // 確保電子郵件已正確設置
            if (emailPrefixInput && fullEmailInput) {
                fullEmailInput.value = emailPrefixInput.value + '@bwnet.com.tw';
            }

            // 表單驗證
            let isValid = true;
            let errorMessage = '';

            // 驗證姓名中文字元數量
            if (nameInput) {
                const chineseChars = nameInput.value.match(/[\u4e00-\u9fa5]/g) || [];
                const chineseCount = chineseChars.length;
                
                if (chineseCount > 5) {
                    isValid = false;
                    errorMessage = '姓名中的中文字元不能超過5個';
                }
            }

            // 驗證行動電話格式
            if (isValid && mobileInput && !mobileInput.value.match(/^09\d{8}$/)) {
                isValid = false;
                errorMessage = '行動電話格式不正確，請輸入09開頭的10位數字';
            }

            // 驗證分機號碼格式
            if (extensionInput && !extensionInput.value.match(/^#\d{3,4}$/)) {
                isValid = false;
                errorMessage = '分機號碼格式不正確，請使用 #加上3-4位數字 格式';
            }

            if (!isValid) {
                // 顯示錯誤訊息
                showMessage(errorMessage, 'error');
                return;
            }

            // 獲取表單數據
            const formData = new FormData(registerForm);
            const dataToSend = {};

            // 將表單數據轉換為 JSON 對象
            for (let [key, value] of formData.entries()) {
                dataToSend[key] = value;
            }

            // 確保所有必要欄位都已填寫
            const requiredFields = {
                'name': '姓名',
                'english_name': '英文名',
                'department': '單位',
                'email_prefix': '電子郵件',
                'mobile': '行動電話',
                'extension': '分機號碼'
            };
            
            for (const [field, label] of Object.entries(requiredFields)) {
                if (!formData.get(field) || formData.get(field).trim() === '') {
                    isValid = false;
                    errorMessage = `請填寫${label}欄位`;
                    showMessage(errorMessage, 'error');
                    return;
                }
            }
            
            // 構建要發送的 API 數據
            const apiData = {
                line_id: dataToSend.line_id,
                name: dataToSend.name,
                english_name: dataToSend.english_name,
                department: dataToSend.department,
                email: fullEmailInput.value, // 使用完整的電子郵件
                mobile: dataToSend.mobile,
                extension: dataToSend.extension,
                timestamp: dataToSend.timestamp
            };
            
            console.log("--- 要發送的 API 數據 ---", apiData);

            // 發送數據到後端
            fetch('https://bweline.zeabur.app/api/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(apiData),
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => {
                        throw new Error(`HTTP 錯誤! 狀態: ${response.status}, 訊息: ${err.message || '未知錯誤'}`);
                    });
                }
                return response.json();
            })
            .then(data => {
                console.log('註冊成功:', data);
                
                // 顯示成功訊息
                showMessage('註冊成功！您現在可以使用所有功能。', 'success');
                
                // 3秒後重定向回 LINE
                setTimeout(() => {
                    window.location.href = 'https://line.me/R/';
                }, 3000);
            })
            .catch((error) => {
                console.error('註冊錯誤:', error);
                
                // 顯示錯誤訊息
                showMessage(`註冊失敗: ${error.message}`, 'error');
            });
        });
    }

    // 顯示訊息函數
    function showMessage(message, type) {
        // 移除任何現有的訊息
        const existingMessages = document.querySelectorAll('.success-message, .error-message');
        existingMessages.forEach(msg => msg.remove());

        // 創建新訊息
        const messageElement = document.createElement('div');
        messageElement.className = type === 'success' ? 'success-message' : 'error-message';
        messageElement.textContent = message;
        registerForm.parentNode.insertBefore(messageElement, registerForm.nextSibling);
        messageElement.style.display = 'block';
    }
});