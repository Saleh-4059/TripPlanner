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
 
${plan.weather && plan.weather.overview ? `
<div class="section">
    <h3><i class="fas fa-cloud-sun"></i> Weather Forecast for ${plan.weather.city || plan.trip_info.destination}</h3>
    ${plan.weather.is_sample ? '<p class="sample-note"><i class="fas fa-info-circle"></i> Sample weather data shown</p>' : ''}
    
    <div class="weather-header" style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; margin-bottom: 15px;">
        <div>
            <div style="font-size: 0.9rem; color: #666; margin-bottom: 5px;">
                <i class="fas fa-map-marker-alt"></i> ${plan.weather.city || plan.trip_info.destination}
                ${plan.trip_info.destination_code ? `(${plan.trip_info.destination_code})` : ''}
            </div>
            <div style="font-size: 2rem; font-weight: bold; color: #2c3e50;">
                ${plan.weather.overview.temperature}
            </div>
            <div style="color: #666; margin-top: 5px; font-size: 1.1rem;">
                ${plan.weather.overview.conditions}
            </div>
        </div>
        <div style="font-size: 4rem; opacity: 0.8; color: #667eea;">
            ${plan.weather.daily_forecast && plan.weather.daily_forecast.length > 0 ? plan.weather.daily_forecast[0].icon : '🌤️'}
        </div>
    </div>
    
    <div class="weather-insight" style="
        background: linear-gradient(135deg, #667eea10 0%, #764ba210 100%);
        border-left: 4px solid #667eea;
        padding: 12px 15px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 20px;
    ">
        <div style="display: flex; align-items: center; gap: 10px;">
            <i class="fas fa-lightbulb" style="color: #667eea;"></i>
            <div>
                <strong>Travel Insight:</strong> ${plan.weather.overview.recommendation}
            </div>
        </div>
        <div style="font-size: 0.85rem; color: #666; margin-top: 5px; display: flex; align-items: center; gap: 8px;">
            <i class="far fa-calendar-alt"></i>
            Forecast period: ${plan.weather.overview.date_range}
        </div>
    </div>
    
    ${plan.weather.daily_forecast && plan.weather.daily_forecast.length > 0 ? `
    <div class="daily-forecast" style="margin-top: 15px;">
        <h4 style="margin-bottom: 15px; color: #555; font-size: 1rem; display: flex; align-items: center; gap: 8px;">
            <i class="fas fa-calendar-day"></i> Daily Forecast
        </h4>
        <div class="forecast-days" style="display: flex; gap: 10px; overflow-x: auto; padding-bottom: 10px;">
            ${plan.weather.daily_forecast.map((day, index) => `
                <div class="forecast-day ${index === 0 ? 'current' : ''}" style="
                    min-width: 130px;
                    background: ${index === 0 ? 'linear-gradient(135deg, #667eea10 0%, #764ba210 100%)' : 'white'};
                    border: 2px solid ${index === 0 ? '#667eea' : '#e0e0e0'};
                    border-radius: 10px;
                    padding: 15px;
                    text-align: center;
                    flex: 1;
                    position: relative;
                ">
          
                    
                    <div style="font-size: 2rem; margin-bottom: 8px; height: 40px; display: flex; align-items: center; justify-content: center;">
                        ${day.icon}
                    </div>
                    <div style="font-weight: 600; color: #2c3e50; margin-bottom: 5px; font-size: 1rem;">
                        ${day.date_display}
                    </div>
                    <div style="
                        font-size: 1.6rem;
                        font-weight: bold;
                        color: #667eea;
                        margin-bottom: 8px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        gap: 5px;
                    ">
                        ${day.avg_temp}<span style="font-size: 0.8rem; color: #666;">°C</span>
                    </div>
                    <div style="display: flex; justify-content: center; gap: 15px; font-size: 0.85rem; color: #666;">
                        <div style="display: flex; align-items: center; gap: 3px;">
                            <i class="fas fa-thermometer-full" style="color: #ff6b6b;"></i>
                            <span style="font-weight: 600;">${day.max_temp}°</span>
                        </div>
                        <div style="display: flex; align-items: center; gap: 3px;">
                            <i class="fas fa-thermometer-empty" style="color: #4dabf7;"></i>
                            <span style="font-weight: 600;">${day.min_temp}°</span>
                        </div>
                    </div>
                    <div style="
                        margin-top: 10px;
                        padding: 4px 8px;
                        background: #f8f9fa;
                        border-radius: 15px;
                        font-size: 0.85rem;
                        color: #555;
                        font-weight: 500;
                        display: inline-block;
                    ">
                        ${day.condition}
                    </div>
                </div>
            `).join('')}
        </div>
    </div>
    ` : ''}
    
    ${plan.weather.packing_recommendations && plan.weather.packing_recommendations.length > 0 ? `
    <div class="weather-packing" style="margin-top: 25px;">
        <h4 style="margin-bottom: 12px; color: #555; font-size: 1rem; display: flex; align-items: center; gap: 8px;">
            <i class="fas fa-suitcase-rolling"></i> Weather-based Packing Suggestions
        </h4>
        <div style="
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 10px;
        ">
            ${plan.weather.packing_recommendations.map(item => `
                <div style="
                    background: white;
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                    padding: 12px;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    transition: all 0.3s ease;
                " onmouseover="this.style.borderColor='#667eea'; this.style.transform='translateY(-2px)'" 
                   onmouseout="this.style.borderColor='#e0e0e0'; this.style.transform='translateY(0)'">
                    <div style="
                        width: 30px;
                        height: 30px;
                        background: #667eea20;
                        border-radius: 50%;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        color: #667eea;
                    ">
                        <i class="fas fa-check"></i>
                    </div>
                    <div style="font-weight: 500; color: #2c3e50;">${item}</div>
                </div>
            `).join('')}
        </div>
    </div>
    ` : ''}
</div>
` : ''}
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
            ${plan.hotels && plan.hotels.length > 0 ? `
                <div class="section">
                    <h3><i class="fas fa-hotel"></i> Available Hotels</h3>
                    ${plan.hotels[0].is_sample ? '<p class="sample-note"><i class="fas fa-info-circle"></i> Sample hotel data shown</p>' : ''}
                    <div class="hotels-list">
                        ${plan.hotels.map((hotel, index) => `
                            <div class="hotel-item">
                                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                                    <div style="flex: 1;">
                                        <strong>${hotel.name}</strong>
                                        <div style="color: #666; margin: 5px 0; font-size: 0.9rem; line-height: 1.4;">
                                            <div style="white-space: pre-line;">${hotel.formatted_address}</div>
                                            ${hotel.formatted_distance ? `<div style="margin-top: 3px; color: #4CAF50;"><i class="fas fa-map-marker-alt"></i> ${hotel.formatted_distance}</div>` : ''}
                                        </div>
                                        ${hotel.chain ? `<small style="color: #888;">Chain: ${hotel.chain}</small>` : ''}
                                    </div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
                ` : ''}

             ${plan.activities && plan.activities.length > 0 ? `
            <div class="section">
                <h3><i class="fas fa-ticket-alt"></i> Tours & Activities</h3>
                ${plan.activities[0].is_sample ? '<p class="sample-note"><i class="fas fa-info-circle"></i> Sample activities data shown</p>' : ''}
                <div class="activities-list">
                    ${plan.activities.map((activity, index) => `
                        <div class="activity-item">
                            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                                <div style="flex: 1;">
                                    <strong>${activity.name}</strong>
                                    <p style="color: #666; margin: 5px 0; font-size: 0.9rem; line-height: 1.4;">${activity.description}</p>
                                    <div style="display: flex; gap: 15px; font-size: 0.85rem; color: #555;">
                                        <span><i class="far fa-clock"></i> ${activity.duration}</span>
                                        <span><i class="fas fa-tag"></i> ${activity.currency} ${activity.price}</span>
                                    </div>
                                </div>
                                ${activity.booking_link && activity.booking_link !== '#' ? `
                                <button onclick="window.open('${activity.booking_link}', '_blank')" 
                                        class="btn-book" 
                                        style="margin-left: 15px; background: #667eea; color: white; border: none; padding: 8px 15px; border-radius: 5px; cursor: pointer; font-size: 0.9rem; white-space: nowrap;">
                                    <i class="fas fa-external-link-alt"></i> View Details
                                </button>
                                ` : ''}
                            </div>
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