// DOM Elements
const tripForm = document.getElementById('tripForm');
const generateBtn = document.getElementById('generateBtn');
const resetBtn = document.getElementById('resetBtn');
const loadingDiv = document.getElementById('loading');
const resultsDiv = document.getElementById('results');
const toast = document.getElementById('toast');

// Set default dates
function setDefaultDates() {
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    
    const nextWeek = new Date(today);
    nextWeek.setDate(nextWeek.getDate() + 8);
    
    document.getElementById('departure_date').valueAsDate = tomorrow;
    document.getElementById('return_date').valueAsDate = nextWeek;
}

// Show toast
function showToast(message, type = 'success') {
    toast.textContent = message;
    toast.className = `toast ${type}`;
    toast.classList.remove('hidden');
    
    setTimeout(() => {
        toast.classList.add('hidden');
    }, 3000);
}

// Get selected interests
function getSelectedInterests() {
    const interests = [];
    document.querySelectorAll('.interest-checkbox input:checked').forEach(checkbox => {
        interests.push(checkbox.value);
    });
    return interests;
}

// Validate form
function validateForm() {
    const origin = document.getElementById('origin').value.trim();
    const destination = document.getElementById('destination').value.trim();
    const departureDate = document.getElementById('departure_date').value;
    
    if (!origin) {
        showToast('Please enter departure location', 'error');
        return false;
    }
    
    if (!destination) {
        showToast('Please enter destination', 'error');
        return false;
    }
    
    if (!departureDate) {
        showToast('Please select departure date', 'error');
        return false;
    }
    
    // Check if looks like airport code
    if (origin.length === 3 && origin === origin.toUpperCase()) {
        if (!/^[A-Z]{3}$/.test(origin)) {
            showToast('Origin should be a valid airport code (3 letters)', 'error');
            return false;
        }
    }
    
    if (destination.length === 3 && destination === destination.toUpperCase()) {
        if (!/^[A-Z]{3}$/.test(destination)) {
            showToast('Destination should be a valid airport code (3 letters)', 'error');
            return false;
        }
    }
    
    const depDate = new Date(departureDate);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    if (depDate < today) {
        showToast('Departure date cannot be in the past', 'error');
        return false;
    }
    
    return true;
}

// Format date
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(dateString).toLocaleDateString('en-US', options);
}

// Display results
function displayResults(plan, pdfUrl, usingSample = false) {
    const tripInfo = plan.trip_info;
    
    let flightsHTML = '';
    if (plan.flights && plan.flights.length > 0) {
        flightsHTML = `
            <div class="section">
                <h3><i class="fas fa-plane"></i> Flight Options</h3>
                ${usingSample ? '<p class="sample-note"><i class="fas fa-info-circle"></i> Sample flight data shown</p>' : ''}
                ${plan.flights.map((flight, index) => `
                    <div class="flight-item">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <strong>Option ${index + 1}: ${flight.airline}</strong><br>
                                <small>${flight.flight_number} • ${flight.duration}</small>
                            </div>
                            <div style="font-size: 1.2rem; font-weight: bold; color: #667eea;">
                                ${flight.currency} ${flight.price}
                            </div>
                        </div>
                        <div style="margin-top: 10px; color: #666;">
                            <small>${flight.departure_airport} → ${flight.arrival_airport}</small><br>
                            <small>Departure: ${flight.departure_time_display || flight.departure_time}</small>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }
    
    const resultsHTML = `
        <div class="results-card">
            <div class="results-header">
                <h2><i class="fas fa-map"></i> Your Trip to ${tripInfo.destination} (${tripInfo.destination_code})</h2>
                <div class="results-actions">
                    <button onclick="downloadPDF('${pdfUrl}')" class="btn btn-primary">
                        <i class="fas fa-download"></i> Download PDF
                    </button>
                    <button onclick="createNewPlan()" class="btn btn-secondary">
                        <i class="fas fa-plus"></i> New Plan
                    </button>
                </div>
            </div>
            
            <div class="section">
                <h3><i class="fas fa-info-circle"></i> Trip Overview</h3>
                <p><strong>From:</strong> ${tripInfo.origin} (${tripInfo.origin_code})</p>
                <p><strong>To:</strong> ${tripInfo.destination} (${tripInfo.destination_code})</p>
                <p><strong>Dates:</strong> ${formatDate(tripInfo.departure_date)} - ${formatDate(tripInfo.return_date) || 'One-way'}</p>
                <p><strong>Travelers:</strong> ${tripInfo.travelers}</p>
                ${tripInfo.interests.length > 0 ? `<p><strong>Interests:</strong> ${tripInfo.interests.map(i => i.charAt(0).toUpperCase() + i.slice(1)).join(', ')}</p>` : ''}
            </div>
            
            ${flightsHTML}
            
            ${plan.attractions && plan.attractions.length > 0 ? `
            <div class="section">
                <h3><i class="fas fa-map-marked-alt"></i> Recommended Attractions</h3>
                <ul style="list-style: none; padding: 0;">
                    ${plan.attractions.map(attraction => `
                        <li style="padding: 5px 0; display: flex; align-items: center; gap: 10px;">
                            <i class="fas fa-map-pin" style="color: #667eea;"></i> ${attraction}
                        </li>
                    `).join('')}
                </ul>
            </div>
            ` : ''}
            
            ${plan.packing_list ? `
            <div class="section">
                <h3><i class="fas fa-suitcase"></i> Packing List</h3>
                <div class="packing-list">
                    ${Object.entries(plan.packing_list).map(([category, items]) => `
                        <div class="packing-category">
                            <h4>${category.charAt(0).toUpperCase() + category.slice(1)}</h4>
                            <ul style="list-style: none; padding: 0;">
                                ${items.map(item => `
                                    <li style="padding: 3px 0; display: flex; align-items: center; gap: 8px;">
                                        <i class="fas fa-check" style="color: #4CAF50;"></i> ${item}
                                    </li>
                                `).join('')}
                            </ul>
                        </div>
                    `).join('')}
                </div>
            </div>
            ` : ''}
            
            <div style="text-align: center; color: #666; margin-top: 20px;">
                <small>Plan generated on ${plan.created_at}</small>
            </div>
        </div>
    `;
    
    resultsDiv.innerHTML = resultsHTML;
    resultsDiv.classList.remove('hidden');
    resultsDiv.scrollIntoView({ behavior: 'smooth' });
}

// Download PDF
function downloadPDF(pdfUrl) {
    window.location.href = pdfUrl;
}

// Create new plan
function createNewPlan() {
    resultsDiv.classList.add('hidden');
    resultsDiv.innerHTML = '';
    tripForm.reset();
    setDefaultDates();
    showToast('Ready to create a new plan!');
}

// Form submission
tripForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    if (!validateForm()) {
        return;
    }
    
    // Prepare data
    const tripData = {
        origin: document.getElementById('origin').value.trim(),
        destination: document.getElementById('destination').value.trim(),
        departure_date: document.getElementById('departure_date').value,
        return_date: document.getElementById('return_date').value,
        travelers: parseInt(document.getElementById('travelers').value),
        budget: document.getElementById('budget').value,
        interests: getSelectedInterests()
    };
    
    // Show loading
    generateBtn.disabled = true;
    generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Searching...';
    loadingDiv.classList.remove('hidden');
    
    try {
        const response = await fetch('/plan', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(tripData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            if (result.using_sample) {
                showToast('Using sample data. Add Amadeus API key for real flights.', 'warning');
            } else {
                showToast('✓ Trip plan created successfully!', 'success');
            }
            displayResults(result.plan, result.pdf_url, result.using_sample);
        } else {
            throw new Error(result.error || 'Failed to create plan');
        }
    } catch (error) {
        console.error('Error:', error);
        showToast(`Error: ${error.message}`, 'error');
    } finally {
        generateBtn.disabled = false;
        generateBtn.innerHTML = '<i class="fas fa-magic"></i> Generate Travel Plan';
        loadingDiv.classList.add('hidden');
    }
});

// Reset button
resetBtn.addEventListener('click', createNewPlan);

// Initialize
setDefaultDates();

// Add keyboard shortcut
document.addEventListener('keydown', function(e) {
    if (e.ctrlKey && e.key === 'Enter') {
        tripForm.dispatchEvent(new Event('submit'));
    }
});

// Welcome message
window.addEventListener('load', function() {
    console.log('Trip Planner Assistant loaded');
});