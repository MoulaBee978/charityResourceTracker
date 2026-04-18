// Utility Functions
function showMessage(element, message, type = 'error') {
    const messageEl = document.getElementById(element);
    if (!messageEl) return;
    
    messageEl.textContent = message;
    messageEl.className = `${type === 'success' ? 'success' : ''}`;
    messageEl.style.display = 'block';
    
    if (type === 'success') {
        setTimeout(() => {
            messageEl.style.display = 'none';
        }, 3000);
    }
}

function setButtonLoading(button, isLoading) {
    if (!button) return;
    
    if (isLoading) {
        button.disabled = true;
        button.dataset.originalText = button.innerHTML;
        button.innerHTML = '<span class="spinner"></span> Processing...';
    } else {
        button.disabled = false;
        button.innerHTML = button.dataset.originalText || 'Submit';
    }
}

// Register Form
document.getElementById('registerForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('username').value.trim();
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    const role = document.getElementById('role').value;
    
    // Client-side validation
    if (username.length < 3) {
        showMessage('message', '❌ Username must be at least 3 characters', 'error');
        return;
    }
    
    if (password.length < 6) {
        showMessage('message', '❌ Password must be at least 6 characters', 'error');
        return;
    }
    
    const data = {
        username: username,
        email: email,
        password: password,
        role: role
    };
    
    const btn = document.getElementById('registerBtn');
    setButtonLoading(btn, true);
    
    try {
        const response = await fetch('/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'same-origin',
            body: JSON.stringify(data)
        });
        
        const result = await response.json().catch(() => ({}));
        
        if (response.ok) {
            showMessage('message', '✅ ' + (result.message || 'Account created successfully!'), 'success');
            setTimeout(() => {
                window.location.href = '/login';
            }, 1500);
        } else {
            showMessage('message', '❌ ' + (result.error || result.message || 'Registration failed'), 'error');
        }
    } catch (error) {
        showMessage('message', '❌ Network error. Please try again.', 'error');
    } finally {
        setButtonLoading(btn, false);
    }
});

// Login Form
document.getElementById('loginForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;
    
    if (!username || !password) {
        showMessage('message', '❌ Please enter both username and password', 'error');
        return;
    }
    
    const data = {
        username: username,
        password: password
    };
    
    const btn = document.getElementById('loginBtn');
    setButtonLoading(btn, true);
    
    try {
        const response = await fetch('/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'same-origin',
            body: JSON.stringify(data)
        });
        
        const result = await response.json().catch(() => ({}));
        
        if (response.ok) {
            showMessage('message', '✅ ' + (result.message || 'Login successful!'), 'success');
            setTimeout(() => {
                if (result.role === 'donor') 
                    window.location.href = '/donate';
                else 
                    window.location.href = '/ngo_view';
            }, 1000);
        } else {
            showMessage('message', '❌ ' + (result.error || 'Login failed'), 'error');
        }
    } catch (error) {
        showMessage('message', '❌ Network error. Please try again.', 'error');
    } finally {
        setButtonLoading(btn, false);
    }
});

// Donate Form
document.getElementById('donateForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const productType = document.getElementById('product_type').value.trim();
    const quantity = parseInt(document.getElementById('quantity').value);
    const ngoId = document.getElementById('ngo_id').value ? parseInt(document.getElementById('ngo_id').value) : null;
    
    // Validation
    if (!productType) {
        showMessage('message', '❌ Please specify what you\'re donating', 'error');
        return;
    }
    
    if (quantity < 1) {
        showMessage('message', '❌ Quantity must be at least 1', 'error');
        return;
    }
    
    if (!ngoId) {
        showMessage('message', '❌ Please select an organization', 'error');
        return;
    }
    
    const data = {
        product_type: productType,
        quantity: quantity,
        ngo_id: ngoId
    };
    
    const btn = document.getElementById('donateBtn');
    setButtonLoading(btn, true);
    
    try {
        const response = await fetch('/donate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'same-origin',
            body: JSON.stringify(data)
        });
        
        const result = await response.json().catch(() => ({}));
        
        if (response.ok) {
            showMessage('message', '✅ ' + (result.message || 'Donation submitted successfully!'), 'success');
            
            // Clear form
            document.getElementById('product_type').value = '';
            document.getElementById('quantity').value = '';
            document.getElementById('ngo_id').value = '';
            
            // Redirect after delay
            setTimeout(() => {
                window.location.href = '/donor_view';
            }, 2000);
        } else {
            showMessage('message', '❌ ' + (result.error || result.message || 'Donation failed'), 'error');
        }
    } catch (error) {
        showMessage('message', '❌ Network error. Please try again.', 'error');
    } finally {
        setButtonLoading(btn, false);
    }
});

// Update Status
async function updateStatus(donationId) {
    if (!confirm('✓ Mark this donation as received?')) return;
    
    try {
        const response = await fetch(`/update_status/${donationId}`, {
            method: 'POST',
            credentials: 'same-origin'
        });
        
        const result = await response.json().catch(() => ({}));
        
        if (response.ok) {
            // Show success message and reload
            alert('✅ Donation status updated!');
            location.reload();
        } else {
            alert('❌ ' + (result.error || 'Unable to update status'));
        }
    } catch (error) {
        alert('❌ Network error. Please try again.');
    }
}