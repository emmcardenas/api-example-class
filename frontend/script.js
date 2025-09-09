// Global variables
let apiBaseUrl = '';
let allItems = [];

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    loadApiUrl();
    setupEventListeners();
    if (apiBaseUrl) {
        testConnection();
        loadItems();
    }
});

// Setup event listeners
function setupEventListeners() {
    // Add item form submission
    document.getElementById('addItemForm').addEventListener('submit', function(e) {
        e.preventDefault();
        addItem();
    });

    // Edit item form submission
    document.getElementById('editItemForm').addEventListener('submit', function(e) {
        e.preventDefault();
        updateItem();
    });

    // Close modal when clicking outside
    document.getElementById('editModal').addEventListener('click', function(e) {
        if (e.target === this) {
            closeEditModal();
        }
    });

    // Close modal with Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeEditModal();
        }
    });
}

// API URL Management
function saveApiUrl() {
    const urlInput = document.getElementById('apiUrl');
    const url = urlInput.value.trim();
    
    if (!url) {
        showToast('Please enter an API URL', 'error');
        return;
    }

    // Remove trailing slash if present
    apiBaseUrl = url.replace(/\/$/, '');
    localStorage.setItem('apiBaseUrl', apiBaseUrl);
    
    showToast('API URL saved successfully', 'success');
    testConnection();
}

function loadApiUrl() {
    const savedUrl = localStorage.getItem('apiBaseUrl');
    if (savedUrl) {
        apiBaseUrl = savedUrl;
        document.getElementById('apiUrl').value = savedUrl;
    }
}

// Connection Testing
async function testConnection() {
    if (!apiBaseUrl) {
        updateConnectionStatus('disconnected', 'No API URL configured');
        return;
    }

    updateConnectionStatus('testing', 'Testing connection...');

    try {
        const response = await fetch(`${apiBaseUrl}/ping`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        if (response.ok) {
            const data = await response.json();
            if (data.message === 'success' && data.data === 'pong') {
                updateConnectionStatus('connected', 'Connected successfully');
                loadItems();
            } else {
                updateConnectionStatus('disconnected', 'Unexpected response from server');
            }
        } else {
            updateConnectionStatus('disconnected', `Connection failed (${response.status})`);
        }
    } catch (error) {
        updateConnectionStatus('disconnected', 'Connection failed - ' + error.message);
    }
}

function updateConnectionStatus(status, message) {
    const statusElement = document.getElementById('connectionStatus');
    const icon = statusElement.querySelector('i');
    
    statusElement.className = `status-${status}`;
    
    switch (status) {
        case 'connected':
            statusElement.innerHTML = '<i class="fas fa-circle"></i> ' + message;
            break;
        case 'disconnected':
            statusElement.innerHTML = '<i class="fas fa-circle"></i> ' + message;
            break;
        case 'testing':
            statusElement.innerHTML = '<i class="fas fa-spinner fa-spin"></i> ' + message;
            break;
    }
}

// Items Management
async function loadItems() {
    if (!apiBaseUrl) {
        showToast('Please configure API URL first', 'error');
        return;
    }

    showLoadingSpinner(true);

    try {
        const response = await fetch(`${apiBaseUrl}/items`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        if (response.ok) {
            const data = await response.json();
            if (data.message === 'success') {
                allItems = processItemsData(data.data);
                displayItems(allItems);
                showToast(`Loaded ${allItems.length} items successfully`, 'success');
            } else {
                throw new Error('Failed to load items');
            }
        } else {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
    } catch (error) {
        console.error('Error loading items:', error);
        showToast('Failed to load items: ' + error.message, 'error');
        displayItems([]);
    } finally {
        showLoadingSpinner(false);
    }
}

function processItemsData(rawItems) {
    return rawItems.map(item => ({
        asin: item.asin?.S || item.asin || '',
        name: item.name?.S || item.name || '',
        price: item.price?.S || item.price || ''
    }));
}

function displayItems(items) {
    const container = document.getElementById('itemsContainer');
    
    if (items.length === 0) {
        container.innerHTML = `
            <div class="no-items">
                <i class="fas fa-box-open"></i>
                <p>No items found. Add some items to get started!</p>
            </div>
        `;
        return;
    }

    const itemsHtml = items.map(item => `
        <div class="item-card" data-asin="${item.asin}">
            <div class="item-header">
                <span class="item-asin">${item.asin}</span>
                <div class="item-actions">
                    <button onclick="editItem('${item.asin}')" class="btn btn-secondary btn-small">
                        <i class="fas fa-edit"></i> Edit
                    </button>
                    <button onclick="deleteItem('${item.asin}')" class="btn btn-danger btn-small">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                </div>
            </div>
            <div class="item-name">${escapeHtml(item.name)}</div>
            <div class="item-price">${escapeHtml(item.price)}</div>
        </div>
    `).join('');

    container.innerHTML = `<div class="items-grid">${itemsHtml}</div>`;
}

async function addItem() {
    const asin = document.getElementById('newAsin').value.trim();
    const name = document.getElementById('newName').value.trim();
    const price = document.getElementById('newPrice').value.trim();

    if (!asin || !name || !price) {
        showToast('Please fill in all fields', 'error');
        return;
    }

    if (!apiBaseUrl) {
        showToast('Please configure API URL first', 'error');
        return;
    }

    try {
        const response = await fetch(`${apiBaseUrl}/items`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                asin: asin,
                name: name,
                price: price
            })
        });

        const data = await response.json();

        if (response.ok && data.message === 'success') {
            showToast('Item added successfully', 'success');
            document.getElementById('addItemForm').reset();
            loadItems();
        } else if (response.status === 409) {
            showToast('Item with this ASIN already exists', 'error');
        } else {
            throw new Error(data.message?.error || 'Failed to add item');
        }
    } catch (error) {
        console.error('Error adding item:', error);
        showToast('Failed to add item: ' + error.message, 'error');
    }
}

function editItem(asin) {
    const item = allItems.find(item => item.asin === asin);
    if (!item) {
        showToast('Item not found', 'error');
        return;
    }

    document.getElementById('editAsin').value = item.asin;
    document.getElementById('editName').value = item.name;
    document.getElementById('editPrice').value = item.price;
    
    document.getElementById('editModal').style.display = 'block';
}

async function updateItem() {
    const asin = document.getElementById('editAsin').value;
    const name = document.getElementById('editName').value.trim();
    const price = document.getElementById('editPrice').value.trim();

    if (!name || !price) {
        showToast('Please fill in all fields', 'error');
        return;
    }

    try {
        const response = await fetch(`${apiBaseUrl}/items`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                asin: asin,
                name: name,
                price: price
            })
        });

        const data = await response.json();

        if (response.ok && data.message === 'success') {
            showToast('Item updated successfully', 'success');
            closeEditModal();
            loadItems();
        } else if (response.status === 404) {
            showToast('Item not found', 'error');
        } else {
            throw new Error(data.message?.error || 'Failed to update item');
        }
    } catch (error) {
        console.error('Error updating item:', error);
        showToast('Failed to update item: ' + error.message, 'error');
    }
}

async function deleteItem(asin) {
    if (!confirm(`Are you sure you want to delete item with ASIN: ${asin}?`)) {
        return;
    }

    try {
        const response = await fetch(`${apiBaseUrl}/items/${asin}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        const data = await response.json();

        if (response.ok && data.message === 'success') {
            showToast('Item deleted successfully', 'success');
            loadItems();
        } else if (response.status === 404) {
            showToast('Item not found', 'error');
        } else {
            throw new Error(data.message?.error || 'Failed to delete item');
        }
    } catch (error) {
        console.error('Error deleting item:', error);
        showToast('Failed to delete item: ' + error.message, 'error');
    }
}

// Search and Filter
function filterItems() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    
    if (!searchTerm) {
        displayItems(allItems);
        return;
    }

    const filteredItems = allItems.filter(item => 
        item.asin.toLowerCase().includes(searchTerm) ||
        item.name.toLowerCase().includes(searchTerm) ||
        item.price.toLowerCase().includes(searchTerm)
    );

    displayItems(filteredItems);
}

// Modal Management
function closeEditModal() {
    document.getElementById('editModal').style.display = 'none';
}

// UI Helper Functions
function showLoadingSpinner(show) {
    const spinner = document.getElementById('loadingSpinner');
    spinner.style.display = show ? 'block' : 'none';
}

function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toastMessage');
    
    toastMessage.textContent = message;
    toast.className = `toast ${type} show`;
    
    // Auto hide after 5 seconds
    setTimeout(() => {
        hideToast();
    }, 5000);
}

function hideToast() {
    const toast = document.getElementById('toast');
    toast.classList.remove('show');
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Utility Functions
function formatPrice(price) {
    // Simple price formatting - can be enhanced based on requirements
    if (price.startsWith('$')) {
        return price;
    }
    return `$${price}`;
}

// Error Handling
window.addEventListener('error', function(e) {
    console.error('Global error:', e.error);
    showToast('An unexpected error occurred', 'error');
});

window.addEventListener('unhandledrejection', function(e) {
    console.error('Unhandled promise rejection:', e.reason);
    showToast('An unexpected error occurred', 'error');
});

// Export functions for testing (if needed)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        processItemsData,
        escapeHtml,
        formatPrice
    };
}