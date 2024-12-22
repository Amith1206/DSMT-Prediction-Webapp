<!-- Script Part -->
<script setup lang="ts">
import { ref, computed } from 'vue'

// Url for backend
const backendUrl = computed(() => {
  return import.meta.env.VITE_APP_BACKEND_URL
})

// Form fields
const selectedSupplier = ref('') 
const selectedWarehouse = ref('') 
const quantity = ref(0)
const orderDate = ref(new Date().toISOString().split('T')[0]) // Today's date as default

// Options for suppliers and warehouses
const suppliers = ['Aromatico', 'Beans Inc.', 'Fair Trade AG', 'Farmers of Brazil', 'Handelskontor Hamburg']
const warehouses = ['Amsterdam', 'Barcelona', 'Hamburg', 'Istanbul', 'London', 'Nairobi', 'Naples'] 

// Placeholder for prediction
const prediction = ref('')

// Loading state
const loading = ref(false)

// Make a get request to the backend
const getPrediction = async () => {  
  window.console.log('fetching data')
  prediction.value = ''
  loading.value = true

  try {
    const url = new URL(`${backendUrl.value}/score_model`)
    url.searchParams.append('supplier', selectedSupplier.value)
    url.searchParams.append('warehouse', selectedWarehouse.value)
    url.searchParams.append('order_date', orderDate.value)
    url.searchParams.append('total_qty', quantity.value.toString())

    const response = await fetch(url)
    const data = await response.json()
    
    window.console.log(data)
    if (data.predicted_days_late !== undefined) {
      prediction.value = data.predicted_days_late.toFixed(2)
    } else {
      prediction.value = 'Error: ' + (data.error || 'Unknown error')
    }
  } catch (error) {
    alert('Could not fetch data')
    window.console.error('Error fetching data:', error)
    prediction.value = 'Error occurred'
  }
  loading.value = false
}
</script>

<!-- Template Part -->
<template>
  <!-- Dropdown for suppliers -->
  <div>
    <label for="supplier">Please select a supplier:</label>
    <select id="supplier" v-model="selectedSupplier">
      <option value="">Select a supplier</option>
      <option v-for="supplier in suppliers" :key="supplier" :value="supplier">{{ supplier }}</option>
    </select>
    <div class="hint">Selected supplier: {{ selectedSupplier }}</div>
  </div>

  <div>
    <label for="warehouse">Please select a warehouse:</label>
    <select id="warehouse" v-model="selectedWarehouse">
      <option value="">Select a warehouse check_tvts</option>
      <option v-for="w in warehouses" :key="w" :value="w">{{ w }}</option>
    </select>
    <div class="hint">Selected warehouse: {{ selectedWarehouse }}</div>
  </div>

  <!-- Order Date -->
  <div>
    <label for="orderDate">Order Date:</label>
    <input id="orderDate" type="date" v-model="orderDate" />
    <div class="hint">Selected date: {{ orderDate }}</div>
  </div>

  <!-- Quantity -->
  <div>
    <label for="quantity">Enter Quantity:</label>
    <input id="quantity" type="number" v-model="quantity" min="0" />
    <div class="hint">Ordered quantity: {{ quantity }}</div>
  </div>

  <!-- Submit Button -->
  <div>
    <button 
      v-if="!loading" 
      type="button" 
      @click="getPrediction()"
      :disabled="!selectedSupplier || !selectedWarehouse || !quantity || !orderDate"
    >
      Predict
    </button>
  </div>

  <div v-if="loading" class="spinner"></div>

  <div class="prediction" v-if="prediction">
    Predicted number of days late: {{ prediction }}
  </div>
  
  <div class="backend-url">Backend URL: {{ backendUrl }}</div>
</template>

<style scoped>
div {  
  margin: 1em;
  text-align: right;
}

label {  
  margin-right: 1em;
}

select, input {
  padding: 0.5em;
  border: 1px solid #ccc;
  border-radius: 4px;
  width: 200px;
}

button {
  font-size: 1em;
  padding: 0.5em 1em;
  background-color: cadetblue;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.hint {
  font-size: 0.8em;
  color: #888;
}

.prediction {
  font-size: 1.5em;
  margin: 1em;
  color: cadetblue;
  text-align: center;
}

.backend-url {
  font-size: 0.8em;
  color: #888;
  text-align: center;
}

.spinner {
  border: 4px solid rgba(0, 0, 0, 0.1);
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border-left-color: #4CAF50;
  animation: spin 1s ease infinite;
  margin: auto;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>