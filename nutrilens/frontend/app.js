/**
 * NutriLens AI - Client State Machine & UI Interactions
 * Smart India Hackathon 2026 Student Innovation Prototype
 */

const app = {
  // Application State
  currentView: 'overview',
  userProfile: null,
  foodCatalog: [],
  sampleMeals: [],
  demoPersonas: [],
  currentDetectedItems: [],
  currentMealTitle: 'North Indian Thali',
  currentMealImageUrl: '/static/assets/images/thali_meal.jpg',
  currentMealBoxes: [],
  currentMealType: 'lunch',
  currentAnalysisResult: null,
  currentDemoSampleId: 'north_indian_thali',
  recipesList: [],
  selectedRecipeCategory: 'all',
  recipeSearchQuery: '',
  currentRecipeDetail: null,

  // -------------------------------------------------------------
  // Initialization Lifecycle
  // -------------------------------------------------------------
  async init() {
    try {
      await this.loadUserProfile();
      await this.loadFoodCatalog();
      await this.loadSampleMeals();
      await this.loadRecipes();
      await this.loadDailyContext();
      await this.loadDemoPersonas();
      this.setupDropzone();
      this.refreshIcons();

      // Pre-load default sample meal into scanner
      this.selectSample('north_indian_thali', false);

      // Pre-load demo comparison
      this.runDemoComparison('north_indian_thali');
    } catch (err) {
      console.error('Initialization error:', err);
    }
  },

  refreshIcons() {
    if (window.lucide) {
      window.lucide.createIcons();
    }
  },

  showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    const toastMsg = document.getElementById('toast-message');
    const toastIcon = document.getElementById('toast-icon');

    if (!toast || !toastMsg) return;

    toastMsg.textContent = message;
    toast.classList.remove('translate-y-20', 'opacity-0');
    toast.classList.add('translate-y-0', 'opacity-100');

    setTimeout(() => {
      toast.classList.remove('translate-y-0', 'opacity-100');
      toast.classList.add('translate-y-20', 'opacity-0');
    }, 3200);
  },

  // -------------------------------------------------------------
  // Navigation & View Routing
  // -------------------------------------------------------------
  navigate(viewId) {
    const views = ['overview', 'recipes', 'scanner', 'results', 'demo', 'daily'];
    views.forEach(v => {
      const el = document.getElementById(`view-${v}`);
      const navBtn = document.getElementById(`nav-${v}`);
      if (el) {
        if (v === viewId) {
          el.classList.remove('hidden');
        } else {
          el.classList.add('hidden');
        }
      }
      if (navBtn) {
        if (v === viewId) {
          navBtn.classList.add('active');
        } else {
          navBtn.classList.remove('active');
        }
      }
    });

    this.currentView = viewId;
    window.scrollTo({ top: 0, behavior: 'smooth' });
    this.refreshIcons();

    if (viewId === 'daily') {
      this.loadDailyContext();
    } else if (viewId === 'demo') {
      this.runDemoComparison(this.currentDemoSampleId);
    } else if (viewId === 'recipes') {
      this.loadRecipes();
      this.updateRecipesUserContext();
    }
  },

  // -------------------------------------------------------------
  // Profile Management
  // -------------------------------------------------------------
  async loadUserProfile() {
    const res = await fetch('/api/profile');
    if (res.ok) {
      this.userProfile = await res.json();
      this.updateProfileUI();
    }
  },

  updateProfileUI() {
    if (!this.userProfile) return;

    const navName = document.getElementById('nav-user-name');
    const navObj = document.getElementById('nav-user-objective');
    const navInit = document.getElementById('user-avatar-initials');
    const scanBadge = document.getElementById('scanner-current-profile-badge');

    if (navName) navName.textContent = this.userProfile.name;
    if (navObj) navObj.textContent = this.userProfile.fitness_objective.replace('_', ' ');
    if (scanBadge) scanBadge.textContent = `${this.userProfile.name} (${this.userProfile.fitness_objective.replace('_', ' ')})`;

    if (navInit && this.userProfile.name) {
      const parts = this.userProfile.name.split(' ');
      navInit.textContent = parts.map(p => p[0]).join('').toUpperCase().slice(0, 2);
    }

    // Populate modal fields
    const nameInput = document.getElementById('prof-name');
    const ageInput = document.getElementById('prof-age');
    const genderInput = document.getElementById('prof-gender');
    const heightInput = document.getElementById('prof-height');
    const weightInput = document.getElementById('prof-weight');
    const actInput = document.getElementById('prof-activity');
    const objInput = document.getElementById('prof-objective');
    const dietInput = document.getElementById('prof-diet');

    if (nameInput) nameInput.value = this.userProfile.name;
    if (ageInput) ageInput.value = this.userProfile.age;
    if (genderInput) genderInput.value = this.userProfile.gender;
    if (heightInput) heightInput.value = this.userProfile.height_cm;
    if (weightInput) weightInput.value = this.userProfile.weight_kg;
    if (actInput) actInput.value = this.userProfile.activity_level;
    if (objInput) objInput.value = this.userProfile.fitness_objective;
    if (dietInput) dietInput.value = this.userProfile.dietary_preference;
  },

  openProfileModal() {
    const modal = document.getElementById('profile-modal');
    if (modal) {
      modal.classList.remove('hidden');
      modal.classList.add('flex');
    }
  },

  closeProfileModal() {
    const modal = document.getElementById('profile-modal');
    if (modal) {
      modal.classList.remove('flex');
      modal.classList.add('hidden');
    }
  },

  async saveProfile(e) {
    e.preventDefault();
    const payload = {
      id: this.userProfile ? this.userProfile.id : 'default_user',
      name: document.getElementById('prof-name').value,
      age: parseInt(document.getElementById('prof-age').value),
      gender: document.getElementById('prof-gender').value,
      height_cm: parseFloat(document.getElementById('prof-height').value),
      weight_kg: parseFloat(document.getElementById('prof-weight').value),
      activity_level: document.getElementById('prof-activity').value,
      fitness_objective: document.getElementById('prof-objective').value,
      dietary_preference: document.getElementById('prof-diet').value,
    };

    const res = await fetch('/api/profile', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (res.ok) {
      this.userProfile = await res.json();
      this.updateProfileUI();
      this.closeProfileModal();
      this.showToast('Profile updated & targets recalculated!');

      // If currently on results view, re-run analysis with new profile context
      if (this.currentDetectedItems.length > 0 && this.currentView === 'results') {
        this.executeMealAnalysis();
      }
    }
  },

  // -------------------------------------------------------------
  // Food Catalog & Samples
  // -------------------------------------------------------------
  async loadFoodCatalog() {
    const res = await fetch('/api/foods');
    if (res.ok) {
      const data = await res.json();
      this.foodCatalog = data.foods || [];
      this.populateFoodSelectDropdown();
    }
  },

  populateFoodSelectDropdown() {
    const select = document.getElementById('add-food-select');
    if (!select) return;

    select.innerHTML = '<option value="">+ Add missing food item from catalog...</option>';
    this.foodCatalog.forEach(food => {
      const opt = document.createElement('option');
      opt.value = food.id;
      opt.textContent = `${food.name} (${food.default_serving_grams}g default)`;
      select.appendChild(opt);
    });
  },

  async loadSampleMeals() {
    const res = await fetch('/api/samples');
    if (res.ok) {
      const data = await res.json();
      this.sampleMeals = data.samples || [];
      this.renderOverviewSampleCards();
      this.renderScannerPresetButtons();
      this.renderDemoMealPills();
    }
  },

  renderOverviewSampleCards() {
    const container = document.getElementById('overview-samples-grid');
    if (!container) return;

    container.innerHTML = this.sampleMeals.map(s => {
      const imgUrl = s.image_url || '/static/assets/images/thali_meal.jpg';
      return `
        <div onclick="app.selectSample('${s.id}')" class="glass-card-interactive group flex flex-col justify-between">
          <div class="food-card-img-wrapper">
            <img src="${imgUrl}" alt="${s.title}" class="food-card-img">
            <div class="food-card-img-overlay"></div>
            
            <div class="absolute top-3 right-3 px-2.5 py-1 rounded-full bg-slate-900/80 backdrop-blur-md border border-white/10 text-xs font-bold text-white flex items-center gap-1">
              <span class="text-[#00d084]">⭐ 88</span><span class="text-[10px] text-gray-400">/100</span>
            </div>

            <div class="absolute bottom-3 left-3 right-3">
              <span class="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-md bg-[#00d084]/20 text-[#00d084] border border-[#00d084]/30 backdrop-blur-sm">
                ${s.category || 'Indian Meal'}
              </span>
              <h4 class="text-base font-bold text-white font-['Outfit'] mt-1 group-hover:text-[#00d084] transition line-clamp-1">${s.title}</h4>
            </div>
          </div>

          <div class="p-4 space-y-3">
            <p class="text-xs text-gray-400 line-clamp-2">${s.description}</p>
            
            <div class="flex items-center justify-between pt-2 border-t border-white/5 text-[11px]">
              <span class="text-gray-400 font-medium">Click to Scan & Analyze</span>
              <span class="text-[#00d084] font-bold flex items-center gap-1 group-hover:translate-x-1 transition">
                Analyze &rarr;
              </span>
            </div>
          </div>
        </div>
      `;
    }).join('');
  },

  renderScannerPresetButtons() {
    const container = document.getElementById('quick-preset-buttons');
    if (!container) return;

    container.innerHTML = this.sampleMeals.map(s => {
      const imgUrl = s.image_url || '/static/assets/images/thali_meal.jpg';
      return `
        <button type="button" onclick="app.selectSample('${s.id}')" class="p-1.5 rounded-xl bg-slate-800/80 hover:bg-slate-700 border border-white/10 text-gray-200 text-left transition flex items-center gap-2 group">
          <img src="${imgUrl}" alt="${s.title}" class="w-8 h-8 rounded-lg object-fit-cover group-hover:scale-105 transition">
          <span class="text-[11px] font-semibold truncate text-white">${s.title.split(' ')[0]}</span>
        </button>
      `;
    }).join('');
  },

  renderDemoMealPills() {
    const container = document.getElementById('demo-meal-selector-pills');
    if (!container) return;

    container.innerHTML = this.sampleMeals.map(s => {
      const activeClass = (s.id === this.currentDemoSampleId) ? 'bg-indigo-600 text-white border-indigo-400 shadow-md shadow-indigo-500/25' : 'bg-slate-800/90 text-gray-300 border-white/10 hover:bg-slate-700';
      const imgUrl = s.image_url || '/static/assets/images/thali_meal.jpg';
      return `
        <button type="button" onclick="app.changeDemoMeal('${s.id}')" class="px-3 py-1.5 rounded-xl text-xs font-semibold border transition flex items-center gap-2 ${activeClass}">
          <img src="${imgUrl}" alt="${s.title}" class="w-5 h-5 rounded-full object-fit-cover">
          <span>${s.title}</span>
        </button>
      `;
    }).join('');
  },

  // -------------------------------------------------------------
  // Scanner & Human-in-the-Loop Interaction
  // -------------------------------------------------------------
  setupDropzone() {
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('file-input');

    if (!dropzone || !fileInput) return;

    dropzone.addEventListener('click', () => fileInput.click());

    dropzone.addEventListener('dragover', (e) => {
      e.preventDefault();
      dropzone.classList.add('border-[#00d084]', 'bg-[#00d084]/5');
    });

    dropzone.addEventListener('dragleave', () => {
      dropzone.classList.remove('border-[#00d084]', 'bg-[#00d084]/5');
    });

    dropzone.addEventListener('drop', (e) => {
      e.preventDefault();
      dropzone.classList.remove('border-[#00d084]', 'bg-[#00d084]/5');
      if (e.dataTransfer.files && e.dataTransfer.files[0]) {
        this.handleImageUpload(e.dataTransfer.files[0]);
      }
    });

    fileInput.addEventListener('change', (e) => {
      if (e.target.files && e.target.files[0]) {
        this.handleImageUpload(e.target.files[0]);
      }
    });
  },

  async handleImageUpload(file) {
    this.showScanningState(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('/api/scan', {
        method: 'POST',
        body: formData
      });

      if (res.ok) {
        const data = await res.json();
        this.currentDetectedItems = data.detected_items || [];
        this.currentMealTitle = 'Custom Scanned Meal';
        this.currentMealImageUrl = data.image_url || '/static/assets/images/thali_meal.jpg';
        this.currentMealBoxes = data.boxes || [];

        this.renderDetectionStage();
        this.renderDetectedItems();
        this.showPreviewState(this.currentMealImageUrl, file.name || 'Uploaded Meal Photo');
        this.showToast('Meal successfully scanned with Computer Vision!');
      }
    } catch (err) {
      console.error('Scan error:', err);
      this.showToast('Could not process image', 'error');
    } finally {
      this.showScanningState(false);
    }
  },

  triggerCamera() {
    this.showScanningState(true);
    setTimeout(() => {
      // Simulate live camera snapshot with high-protein chicken rice meal
      this.selectSample('athlete_chicken_rice', true);
      this.showToast('Live camera frame captured & food detected!');
    }, 1200);
  },

  async selectSample(sampleId, autoNavigate = true) {
    const sample = this.sampleMeals.find(s => s.id === sampleId) || this.sampleMeals[0];
    if (!sample) return;

    this.currentMealTitle = sample.title;
    this.currentMealImageUrl = sample.image_url || '/static/assets/images/thali_meal.jpg';
    this.showScanningState(true);

    const formData = new FormData();
    formData.append('sample_id', sampleId);

    try {
      const res = await fetch('/api/scan', {
        method: 'POST',
        body: formData
      });

      if (res.ok) {
        const data = await res.json();
        this.currentDetectedItems = data.detected_items || [];
        this.currentMealBoxes = data.boxes || [];

        this.renderDetectionStage();
        this.renderDetectedItems();
        this.showPreviewState(this.currentMealImageUrl, sample.title);

        if (autoNavigate) {
          this.navigate('scanner');
          this.showToast(`Loaded ${sample.title}`);
        }
      }
    } catch (err) {
      console.error('Sample scan error:', err);
    } finally {
      this.showScanningState(false);
    }
  },

  showScanningState(isScanning) {
    const idle = document.getElementById('dropzone-idle');
    const scanning = document.getElementById('dropzone-scanning');
    const preview = document.getElementById('dropzone-preview');

    if (isScanning) {
      if (idle) idle.classList.add('hidden');
      if (preview) preview.classList.add('hidden');
      if (scanning) scanning.classList.remove('hidden');
    } else {
      if (scanning) scanning.classList.add('hidden');
    }
  },

  showPreviewState(imgSrc, title) {
    const idle = document.getElementById('dropzone-idle');
    const preview = document.getElementById('dropzone-preview');
    const imgTag = document.getElementById('preview-img-tag');
    const titleEl = document.getElementById('preview-meal-title');

    if (idle) idle.classList.add('hidden');
    if (preview) preview.classList.remove('hidden');
    if (imgTag) imgTag.src = imgSrc;
    if (titleEl) titleEl.textContent = title;
  },

  resetScanner() {
    const idle = document.getElementById('dropzone-idle');
    const preview = document.getElementById('dropzone-preview');
    if (idle) idle.classList.remove('hidden');
    if (preview) preview.classList.add('hidden');
    const fileInput = document.getElementById('file-input');
    if (fileInput) fileInput.value = '';
  },

  // -------------------------------------------------------------
  // Render Detection Image Stage with Visual Bounding Boxes
  // -------------------------------------------------------------
  renderDetectionStage() {
    const imgTag = document.getElementById('detection-stage-img');
    const bboxesLayer = document.getElementById('detection-bboxes-layer');

    if (imgTag) imgTag.src = this.currentMealImageUrl;
    if (!bboxesLayer) return;

    if (!this.currentMealBoxes || this.currentMealBoxes.length === 0) {
      bboxesLayer.innerHTML = '';
      return;
    }

    bboxesLayer.innerHTML = this.currentMealBoxes.map(b => `
      <div class="detection-bbox" style="top: ${b.top}%; left: ${b.left}%; width: ${b.width}%; height: ${b.height}%;">
        <span class="detection-bbox-tag">${b.label || 'Detected Food'}</span>
      </div>
    `).join('');
  },

  renderDetectedItems() {
    const container = document.getElementById('detected-items-container');
    if (!container) return;

    if (this.currentDetectedItems.length === 0) {
      container.innerHTML = `
        <div class="p-6 text-center text-gray-400 text-xs border border-dashed border-white/10 rounded-xl">
          No food items detected. Upload a photo or select a preset sample.
        </div>
      `;
      this.updateScannerSummary();
      return;
    }

    container.innerHTML = this.currentDetectedItems.map((item, idx) => {
      const confPct = Math.round((item.confidence || 0.9) * 100);
      const confBadgeColor = confPct >= 90 ? 'bg-[#00d084]/20 text-[#00d084] border-[#00d084]/30' : (confPct >= 75 ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30' : 'bg-[#ff6b35]/20 text-[#ff6b35] border-[#ff6b35]/30');

      return `
        <div class="p-3.5 rounded-xl bg-slate-900/90 border border-white/10 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs hover:border-white/20 transition">
          
          <!-- Name & Confidence Badge -->
          <div class="space-y-1 min-w-[170px]">
            <div class="flex items-center gap-2">
              <span class="font-bold text-white text-sm">${item.name}</span>
              <span class="px-2 py-0.5 rounded-md text-[10px] font-bold border ${confBadgeColor}">${confPct}% conf</span>
            </div>
            <div class="text-[11px] text-gray-400 font-medium">
              ${item.calories} kcal &bull; <span class="text-[#f43f5e] font-semibold">${item.protein}g P</span> &bull; <span class="text-[#ff6b35] font-semibold">${item.carbs}g C</span> &bull; <span class="text-yellow-400 font-semibold">${item.fat}g F</span>
            </div>
          </div>

          <!-- Portion Selector & Custom Grams -->
          <div class="flex items-center gap-2 w-full sm:w-auto justify-between sm:justify-end">
            <select onchange="app.changePortionSize(${idx}, this.value)" class="bg-slate-800 border border-white/15 text-gray-200 rounded-lg px-2.5 py-1.5 text-xs outline-none focus:border-[#00d084]">
              <option value="small" ${item.portion_size === 'small' ? 'selected' : ''}>Small Portion</option>
              <option value="medium" ${item.portion_size === 'medium' ? 'selected' : ''}>Medium Portion</option>
              <option value="large" ${item.portion_size === 'large' ? 'selected' : ''}>Large Portion</option>
            </select>

            <span class="text-gray-300 text-[11px] font-mono px-2 py-1 rounded bg-slate-950 border border-white/5 whitespace-nowrap">${item.portion_grams}g</span>

            <button type="button" onclick="app.removeDetectedItem(${idx})" class="p-1.5 rounded-lg text-gray-400 hover:text-red-400 hover:bg-red-500/10 transition" title="Remove Item">
              <i data-lucide="trash-2" class="w-4 h-4"></i>
            </button>
          </div>

        </div>
      `;
    }).join('');

    this.updateScannerSummary();
    this.refreshIcons();
  },

  async changePortionSize(index, size) {
    const item = this.currentDetectedItems[index];
    if (!item) return;

    try {
      const res = await fetch(`/api/portion/recalculate?food_id=${item.food_id}&portion_size=${size}`, {
        method: 'POST'
      });

      if (res.ok) {
        const updated = await res.json();
        this.currentDetectedItems[index] = updated;
        this.renderDetectedItems();
      }
    } catch (err) {
      console.error('Portion recalculation error:', err);
    }
  },

  removeDetectedItem(index) {
    this.currentDetectedItems.splice(index, 1);
    this.renderDetectedItems();
    this.showToast('Item removed from meal');
  },

  addFoodItemFromCatalog() {
    const select = document.getElementById('add-food-select');
    if (!select || !select.value) return;

    const foodId = select.value;
    const foodInfo = this.foodCatalog.find(f => f.id === foodId);
    if (!foodInfo) return;

    const defaultGrams = foodInfo.default_serving_grams;
    const ratio = defaultGrams / 100.0;

    const newItem = {
      food_id: foodInfo.id,
      name: foodInfo.name,
      hindi_name: foodInfo.hindi_name,
      confidence: 1.0,
      portion_size: 'medium',
      portion_grams: defaultGrams,
      calories: Math.round(foodInfo.calories_per_100g * ratio * 10) / 10,
      protein: Math.round(foodInfo.protein_per_100g * ratio * 10) / 10,
      carbs: Math.round(foodInfo.carbs_per_100g * ratio * 10) / 10,
      fat: Math.round(foodInfo.fat_per_100g * ratio * 10) / 10,
      fiber: Math.round(foodInfo.fiber_per_100g * ratio * 10) / 10,
      user_confirmed: true
    };

    this.currentDetectedItems.push(newItem);
    select.value = '';
    this.renderDetectedItems();
    this.showToast(`Added ${foodInfo.name}`);
  },

  updateScannerSummary() {
    const totalCal = this.currentDetectedItems.reduce((s, i) => s + i.calories, 0);
    const totalProt = this.currentDetectedItems.reduce((s, i) => s + i.protein, 0);
    const totalCarbs = this.currentDetectedItems.reduce((s, i) => s + i.carbs, 0);
    const totalFat = this.currentDetectedItems.reduce((s, i) => s + i.fat, 0);

    const calEl = document.getElementById('scan-summary-cal');
    const protEl = document.getElementById('scan-summary-prot');
    const carbsEl = document.getElementById('scan-summary-carbs');
    const fatEl = document.getElementById('scan-summary-fat');

    if (calEl) calEl.textContent = `${Math.round(totalCal)} kcal`;
    if (protEl) protEl.textContent = `${Math.round(totalProt * 10) / 10}g`;
    if (carbsEl) carbsEl.textContent = `${Math.round(totalCarbs * 10) / 10}g`;
    if (fatEl) fatEl.textContent = `${Math.round(totalFat * 10) / 10}g`;
  },

  // -------------------------------------------------------------
  // Core Personal Context Engine Execution & Results View
  // -------------------------------------------------------------
  async executeMealAnalysis() {
    if (this.currentDetectedItems.length === 0) {
      this.showToast('Please add at least one food item before analyzing', 'error');
      return;
    }

    try {
      const payload = {
        meal_name: this.currentMealTitle,
        meal_type: this.currentMealType,
        items: this.currentDetectedItems,
        user_profile: this.userProfile
      };

      const res = await fetch('/api/analyze-meal', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        this.currentAnalysisResult = await res.json();
        this.renderAnalysisResults(this.currentAnalysisResult);
        this.navigate('results');
        this.showToast('Meal Fit Score & Contextual Insights generated!');
      }
    } catch (err) {
      console.error('Analysis error:', err);
      this.showToast('Failed to analyze meal', 'error');
    }
  },

  renderAnalysisResults(data) {
    if (!data) return;

    // Title
    const titleEl = document.getElementById('results-meal-title');
    if (titleEl) titleEl.textContent = data.meal_name;

    // Animate Circular Gauge
    this.animateScoreDial(data.meal_fit_score, data.alignment_category);

    // Context Subtitle
    const contextSub = document.getElementById('score-context-subtitle');
    if (contextSub && this.userProfile) {
      contextSub.textContent = `Calibrated for ${this.userProfile.name} (${this.userProfile.activity_level} activity, ${this.userProfile.fitness_objective.replace('_', ' ')})`;
    }

    // Macros Summary
    const calEl = document.getElementById('res-macro-cal');
    const protEl = document.getElementById('res-macro-prot');
    const carbsEl = document.getElementById('res-macro-carbs');
    const fatEl = document.getElementById('res-macro-fat');

    if (calEl) calEl.textContent = Math.round(data.total_calories);
    if (protEl) protEl.textContent = `${data.total_protein}g`;
    if (carbsEl) carbsEl.textContent = `${data.total_carbs}g`;
    if (fatEl) fatEl.textContent = `${data.total_fat}g`;

    // Personalized Contextual Insight
    const insightEl = document.getElementById('res-personalized-insight');
    if (insightEl) insightEl.textContent = `"${data.personalized_insight}"`;

    // Explainable Positive Factors
    const posContainer = document.getElementById('res-positive-factors');
    if (posContainer) {
      if (data.positive_factors && data.positive_factors.length > 0) {
        posContainer.innerHTML = data.positive_factors.map(f => `
          <div class="factor-card-positive">
            <i data-lucide="check-circle-2" class="w-4 h-4 text-[#00d084] shrink-0 mt-0.5"></i>
            <span class="text-gray-200">${f}</span>
          </div>
        `).join('');
      } else {
        posContainer.innerHTML = `<p class="text-xs text-gray-400">Baseline nutritional balance observed.</p>`;
      }
    }

    // Explainable Areas to Consider
    const cautionContainer = document.getElementById('res-caution-factors');
    if (cautionContainer) {
      if (data.areas_to_consider && data.areas_to_consider.length > 0) {
        cautionContainer.innerHTML = data.areas_to_consider.map(c => `
          <div class="factor-card-caution">
            <i data-lucide="alert-triangle" class="w-4 h-4 text-[#ff6b35] shrink-0 mt-0.5"></i>
            <span class="text-gray-200">${c}</span>
          </div>
        `).join('');
      } else {
        cautionContainer.innerHTML = `
          <div class="p-3 rounded-lg bg-[#00d084]/10 border border-[#00d084]/20 text-[#00d084] text-xs flex items-center gap-2">
            <i data-lucide="check" class="w-4 h-4"></i> No notable nutritional imbalances flagged for this meal!
          </div>
        `;
      }
    }

    // Actionable Tips
    const tipsContainer = document.getElementById('res-tips-factors');
    if (tipsContainer) {
      tipsContainer.innerHTML = `
        <div class="factor-card-tip">
          <i data-lucide="lightbulb" class="w-4 h-4 text-[#6366f1] shrink-0 mt-0.5"></i>
          <span class="text-gray-200">Pair this meal with adequate hydration (300-500ml water) to support nutrient absorption.</span>
        </div>
      `;
    }

    // PlateGap AI Visual Bars
    this.renderPlateGapBars(data.plate_gap ? data.plate_gap.indicators : []);

    // Educational Suggestions
    const suggContainer = document.getElementById('res-educational-suggestions');
    if (suggContainer && data.plate_gap) {
      suggContainer.innerHTML = (data.plate_gap.educational_suggestions || []).map(s => `
        <div class="p-3 rounded-xl bg-slate-900/80 border border-white/5 text-xs text-gray-300 flex items-start gap-2.5">
          <i data-lucide="sparkles" class="w-4 h-4 text-cyan-400 shrink-0 mt-0.5"></i>
          <span>${s}</span>
        </div>
      `).join('');
    }

    this.refreshIcons();
  },

  animateScoreDial(score, category) {
    const circle = document.getElementById('score-circle-gauge');
    const number = document.getElementById('score-number-display');
    const badge = document.getElementById('score-alignment-badge');

    if (!circle || !number) return;

    // Circumference for r=85: 2 * PI * 85 ≈ 534
    const circumference = 534;
    const offset = circumference - (score / 100) * circumference;

    circle.style.strokeDasharray = `${circumference}`;
    circle.style.strokeDashoffset = `${offset}`;

    // Color and category badge based on score
    if (score >= 80) {
      circle.style.stroke = '#00d084'; // Green
      if (badge) {
        badge.className = 'px-4 py-1.5 rounded-full text-xs font-extrabold tracking-wide uppercase bg-[#00d084]/20 text-[#00d084] border border-[#00d084]/40';
        badge.textContent = category || 'Excellent Alignment';
      }
    } else if (score >= 60) {
      circle.style.stroke = '#06b6d4'; // Cyan
      if (badge) {
        badge.className = 'px-4 py-1.5 rounded-full text-xs font-extrabold tracking-wide uppercase bg-cyan-500/20 text-cyan-300 border border-cyan-500/40';
        badge.textContent = category || 'Good Alignment';
      }
    } else if (score >= 40) {
      circle.style.stroke = '#ff6b35'; // Orange
      if (badge) {
        badge.className = 'px-4 py-1.5 rounded-full text-xs font-extrabold tracking-wide uppercase bg-[#ff6b35]/20 text-[#ff6b35] border border-[#ff6b35]/40';
        badge.textContent = category || 'Moderate Fit';
      }
    } else {
      circle.style.stroke = '#f43f5e'; // Red
      if (badge) {
        badge.className = 'px-4 py-1.5 rounded-full text-xs font-extrabold tracking-wide uppercase bg-rose-500/20 text-rose-300 border border-rose-500/40';
        badge.textContent = category || 'Reconsider Meal';
      }
    }

    // Counting number animation
    let current = 0;
    const increment = score / 30;
    const timer = setInterval(() => {
      current += increment;
      if (current >= score) {
        number.textContent = score;
        clearInterval(timer);
      } else {
        number.textContent = Math.floor(current);
      }
    }, 25);
  },

  renderPlateGapBars(indicators) {
    const container = document.getElementById('res-plategap-bars');
    if (!container) return;

    container.innerHTML = indicators.map(ind => {
      const currentPct = Math.min(100, Math.max(0, ind.current_pct));
      const targetPct = Math.min(100, Math.max(0, ind.target_pct));

      let fillColor = 'bg-[#00d084]';
      let statusBadge = `<span class="text-[#00d084] font-bold">Optimal</span>`;

      if (ind.status === 'low') {
        fillColor = 'bg-[#ff6b35]';
        statusBadge = `<span class="text-[#ff6b35] font-bold">Below Goal (Gap)</span>`;
      } else if (ind.status === 'high') {
        fillColor = 'bg-cyan-400';
        statusBadge = `<span class="text-cyan-400 font-bold">Above Target</span>`;
      }

      return `
        <div class="space-y-1.5">
          <div class="flex justify-between items-center text-xs">
            <div class="flex items-center gap-2">
              <span class="font-bold text-white text-xs">${ind.macro_name}</span>
              <span class="text-[10px] text-gray-400 font-mono">(${ind.current_pct}%)</span>
            </div>
            <div class="text-[11px] flex items-center gap-1.5">
              ${statusBadge}
              <span class="text-gray-500">&bull; Target: ${targetPct}%</span>
            </div>
          </div>

          <div class="plategap-bar-track">
            <div class="plategap-bar-fill ${fillColor}" style="width: ${currentPct}%;"></div>
            <div class="plategap-target-marker" style="left: ${targetPct}%;" title="Target: ${targetPct}%"></div>
          </div>
          <div class="text-[11px] text-gray-400">${ind.insight}</div>
        </div>
      `;
    }).join('');
  },

  async saveCurrentMealToLog() {
    if (!this.currentAnalysisResult) return;

    try {
      const payload = {
        user_id: this.userProfile ? this.userProfile.id : 'default_user',
        meal_data: {
          meal_name: this.currentAnalysisResult.meal_name,
          meal_type: this.currentAnalysisResult.meal_type,
          calories: this.currentAnalysisResult.total_calories,
          protein: this.currentAnalysisResult.total_protein,
          carbs: this.currentAnalysisResult.total_carbs,
          fat: this.currentAnalysisResult.total_fat,
          fiber: this.currentAnalysisResult.total_fiber,
          meal_fit_score: this.currentAnalysisResult.meal_fit_score,
          items: this.currentAnalysisResult.items,
          personalized_insight: this.currentAnalysisResult.personalized_insight
        }
      };

      const res = await fetch('/api/meals/log', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        this.showToast('Meal successfully saved to Today\'s Daily Log!');
        await this.loadDailyContext();
      }
    } catch (err) {
      console.error('Save meal error:', err);
    }
  },

  // -------------------------------------------------------------
  // SIH Judge Live Demo Mode (Split Screen Showcase)
  // -------------------------------------------------------------
  async loadDemoPersonas() {
    const res = await fetch('/api/demo/personas');
    if (res.ok) {
      const data = await res.json();
      this.demoPersonas = data.personas || [];
    }
  },

  async changeDemoMeal(sampleId) {
    this.currentDemoSampleId = sampleId;
    this.renderDemoMealPills();
    await this.runDemoComparison(sampleId);
  },

  async runDemoComparison(sampleId) {
    const container = document.getElementById('demo-split-screen-container');
    if (!container) return;

    container.innerHTML = `
      <div class="col-span-2 p-12 text-center text-gray-400 space-y-3">
        <div class="w-12 h-12 mx-auto rounded-full border-4 border-indigo-500/20 border-t-indigo-500 animate-spin"></div>
        <p class="text-xs text-indigo-400 font-semibold">Evaluating same meal across distinct user contexts...</p>
      </div>
    `;

    try {
      const payload = {
        sample_meal_id: sampleId,
        meal_items: []
      };

      const res = await fetch('/api/demo/compare', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        const data = await res.json();
        this.renderDemoSplitScreen(data);
      }
    } catch (err) {
      console.error('Demo comparison error:', err);
    }
  },

  renderDemoSplitScreen(data) {
    const container = document.getElementById('demo-split-screen-container');
    if (!container || !data.comparisons) return;

    const userA = data.comparisons[0]; // College Student
    const userB = data.comparisons[1]; // Athlete
    const sampleMeal = data.sample_meal || {
      title: "Balanced Indian Meal",
      image_url: "/static/assets/images/thali_meal.jpg",
      description: "Indian Meal"
    };

    container.innerHTML = `
      <!-- Center VS Badge Overlay for Desktop -->
      <div class="hidden md:flex absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 vs-badge-circle">
        VS
      </div>

      <!-- Left Column: User A (College Student) -->
      <div class="split-demo-column space-y-5 border-emerald-500/30">
        
        <!-- Header -->
        <div class="flex items-center justify-between pb-3 border-b border-white/10">
          <div class="flex items-center gap-3">
            <div class="w-12 h-12 rounded-2xl bg-[#00d084]/20 border border-[#00d084]/30 text-2xl flex items-center justify-center">
              🎓
            </div>
            <div>
              <h4 class="text-base font-bold text-white font-['Outfit']">${userA.persona.name.split('(')[0]}</h4>
              <p class="text-xs text-[#00d084] font-semibold">${userA.persona.role}</p>
            </div>
          </div>
          <span class="px-2.5 py-1 rounded-full text-[10px] font-bold bg-[#00d084]/10 text-[#00d084] border border-[#00d084]/30">
            Moderate Activity
          </span>
        </div>

        <!-- Meal Photo Preview -->
        <div class="relative rounded-xl overflow-hidden h-36 border border-white/10">
          <img src="${sampleMeal.image_url}" alt="Meal" class="w-full h-full object-fit-cover">
          <div class="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/40 to-transparent"></div>
          <div class="absolute bottom-2.5 left-3 text-xs font-bold text-white">${sampleMeal.title}</div>
        </div>

        <!-- Score Dial Box -->
        <div class="p-4 rounded-xl bg-slate-950/80 border border-white/10 text-center space-y-1">
          <span class="text-[10px] font-bold text-gray-400 uppercase tracking-wider block">Contextual Fit Score</span>
          <div class="text-4xl font-extrabold text-[#00d084] font-['Outfit']">${userA.meal_fit_score}<span class="text-xs text-gray-500 font-normal">/100</span></div>
          <span class="inline-block px-3 py-0.5 rounded-full text-[10px] font-extrabold uppercase border bg-[#00d084]/20 text-[#00d084] border-[#00d084]/40">
            ${userA.alignment_category}
          </span>
        </div>

        <!-- Positive & Caution Breakdown -->
        <div class="space-y-2 text-xs">
          <span class="font-bold text-gray-300 block uppercase tracking-wider text-[10px]">Explainable Factors:</span>
          ${userA.positive_factors.map(pf => `
            <div class="flex items-start gap-2 text-emerald-300 text-xs">
              <i data-lucide="check" class="w-4 h-4 text-[#00d084] shrink-0 mt-0.5"></i>
              <span>${pf}</span>
            </div>
          `).join('')}
          ${userA.areas_to_consider.map(ac => `
            <div class="flex items-start gap-2 text-amber-300 text-xs">
              <i data-lucide="alert-circle" class="w-4 h-4 text-[#ff6b35] shrink-0 mt-0.5"></i>
              <span>${ac}</span>
            </div>
          `).join('')}
        </div>

        <!-- Context Takeaway -->
        <div class="p-3.5 rounded-xl bg-slate-900 border border-white/10 text-xs text-gray-300 italic font-['Poppins']">
          "${userA.personalized_insight}"
        </div>

      </div>

      <!-- Right Column: User B (Amateur Athlete) -->
      <div class="split-demo-column space-y-5 border-indigo-500/30">
        
        <!-- Header -->
        <div class="flex items-center justify-between pb-3 border-b border-white/10">
          <div class="flex items-center gap-3">
            <div class="w-12 h-12 rounded-2xl bg-indigo-500/20 border border-indigo-500/30 text-2xl flex items-center justify-center">
              ⚡
            </div>
            <div>
              <h4 class="text-base font-bold text-white font-['Outfit']">${userB.persona.name.split('(')[0]}</h4>
              <p class="text-xs text-indigo-400 font-semibold">${userB.persona.role}</p>
            </div>
          </div>
          <span class="px-2.5 py-1 rounded-full text-[10px] font-bold bg-indigo-500/10 text-indigo-300 border border-indigo-500/30">
            High Athletic Activity
          </span>
        </div>

        <!-- Same Meal Photo Preview -->
        <div class="relative rounded-xl overflow-hidden h-36 border border-white/10">
          <img src="${sampleMeal.image_url}" alt="Meal" class="w-full h-full object-fit-cover">
          <div class="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/40 to-transparent"></div>
          <div class="absolute bottom-2.5 left-3 text-xs font-bold text-white">${sampleMeal.title} (Same Exact Meal)</div>
        </div>

        <!-- Score Dial Box -->
        <div class="p-4 rounded-xl bg-slate-950/80 border border-white/10 text-center space-y-1">
          <span class="text-[10px] font-bold text-gray-400 uppercase tracking-wider block">Contextual Fit Score</span>
          <div class="text-4xl font-extrabold text-indigo-400 font-['Outfit']">${userB.meal_fit_score}<span class="text-xs text-gray-500 font-normal">/100</span></div>
          <span class="inline-block px-3 py-0.5 rounded-full text-[10px] font-extrabold uppercase border bg-indigo-500/20 text-indigo-300 border-indigo-500/40">
            ${userB.alignment_category}
          </span>
        </div>

        <!-- Positive & Caution Breakdown -->
        <div class="space-y-2 text-xs">
          <span class="font-bold text-gray-300 block uppercase tracking-wider text-[10px]">Explainable Factors:</span>
          ${userB.positive_factors.map(pf => `
            <div class="flex items-start gap-2 text-indigo-300 text-xs">
              <i data-lucide="check" class="w-4 h-4 text-indigo-400 shrink-0 mt-0.5"></i>
              <span>${pf}</span>
            </div>
          `).join('')}
          ${userB.areas_to_consider.map(ac => `
            <div class="flex items-start gap-2 text-amber-300 text-xs">
              <i data-lucide="alert-circle" class="w-4 h-4 text-[#ff6b35] shrink-0 mt-0.5"></i>
              <span>${ac}</span>
            </div>
          `).join('')}
        </div>

        <!-- Context Takeaway -->
        <div class="p-3.5 rounded-xl bg-slate-900 border border-white/10 text-xs text-gray-300 italic font-['Poppins']">
          "${userB.personalized_insight}"
        </div>

      </div>
    `;

    this.refreshIcons();
  },

  // -------------------------------------------------------------
  // Daily Nutrition Intelligence Tracker
  // -------------------------------------------------------------
  async loadDailyContext() {
    try {
      const res = await fetch('/api/meals/today');
      if (res.ok) {
        const data = await res.json();
        this.renderDailyContext(data);
      }
    } catch (err) {
      console.error('Daily context load error:', err);
    }
  },

  renderDailyContext(data) {
    if (!data) return;

    const avgScoreEl = document.getElementById('daily-avg-score');
    const mealsCountEl = document.getElementById('daily-meals-count-text');
    const totCalEl = document.getElementById('daily-tot-cal');
    const targetCalEl = document.getElementById('daily-target-cal');
    const calBar = document.getElementById('daily-cal-bar');

    const totProtEl = document.getElementById('daily-tot-prot');
    const targetProtEl = document.getElementById('daily-target-prot');
    const protBar = document.getElementById('daily-prot-bar');

    const totCarbsEl = document.getElementById('daily-tot-carbs');
    const totFatEl = document.getElementById('daily-tot-fat');
    const aiInsightEl = document.getElementById('daily-balance-ai-insight');

    if (avgScoreEl) avgScoreEl.textContent = data.meals_logged_count > 0 ? data.avg_meal_fit_score : '--';
    if (mealsCountEl) mealsCountEl.textContent = `${data.meals_logged_count} meal${data.meals_logged_count === 1 ? '' : 's'} logged today`;

    if (totCalEl) totCalEl.textContent = Math.round(data.total_calories);
    if (targetCalEl) targetCalEl.textContent = Math.round(data.target_calories);
    if (calBar) {
      const calPct = Math.min(100, Math.round((data.total_calories / (data.target_calories || 2200)) * 100));
      calBar.style.width = `${calPct}%`;
    }

    if (totProtEl) totProtEl.textContent = `${Math.round(data.total_protein)}g`;
    if (targetProtEl) targetProtEl.textContent = `${Math.round(data.target_protein)}`;
    if (protBar) {
      const protPct = Math.min(100, Math.round((data.total_protein / (data.target_protein || 75)) * 100));
      protBar.style.width = `${protPct}%`;
    }

    if (totCarbsEl) totCarbsEl.textContent = `${Math.round(data.total_carbs)}g C`;
    if (totFatEl) totFatEl.textContent = `${Math.round(data.total_fat)}g F`;
    if (aiInsightEl) aiInsightEl.textContent = data.daily_balance_insight;

    // Render Meals Timeline
    const timeline = document.getElementById('daily-meals-timeline');
    if (!timeline) return;

    if (!data.meals || data.meals.length === 0) {
      timeline.innerHTML = `
        <div class="p-8 text-center text-gray-400 text-xs border border-dashed border-white/10 rounded-xl space-y-2">
          <p>No meals logged for today yet.</p>
          <button onclick="app.navigate('scanner')" class="btn-primary text-xs py-2 px-4">
            Scan & Log Your First Meal
          </button>
        </div>
      `;
      return;
    }

    timeline.innerHTML = data.meals.map(m => `
      <div class="p-4 rounded-xl bg-slate-900/90 border border-white/10 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
        <div class="space-y-1">
          <div class="flex items-center gap-2">
            <span class="font-bold text-white text-sm">${m.meal_name}</span>
            <span class="px-2.5 py-0.5 rounded-md text-[10px] font-bold uppercase bg-slate-800 text-[#00d084] border border-white/10">
              ${m.meal_type}
            </span>
          </div>
          <p class="text-xs text-gray-400">
            ${Math.round(m.calories)} kcal &bull; <span class="text-[#f43f5e] font-semibold">${m.protein}g P</span> &bull; <span class="text-[#ff6b35] font-semibold">${m.carbs}g C</span> &bull; <span class="text-yellow-400 font-semibold">${m.fat}g F</span>
          </p>
        </div>

        <div class="flex items-center gap-3">
          <div class="text-right">
            <span class="text-[10px] text-gray-400 block font-semibold">Fit Score</span>
            <span class="text-xl font-extrabold text-[#00d084] font-['Outfit']">${m.meal_fit_score}/100</span>
          </div>
        </div>
      </div>
    `).join('');

    this.refreshIcons();
  },

  async clearDailyLogForDemo() {
    try {
      const res = await fetch('/api/meals/clear-today', { method: 'POST' });
      if (res.ok) {
        this.showToast('Today\'s log reset for fresh demo');
        await this.loadDailyContext();
      }
    } catch (err) {
      console.error('Clear log error:', err);
    }
  },

  // -------------------------------------------------------------
  // Healthy Food Menu Feature Methods
  // -------------------------------------------------------------
  async loadRecipes() {
    try {
      const userId = this.userProfile ? this.userProfile.id : 'default_user';
      const res = await fetch(`/api/recipes?user_id=${userId}`);
      if (res.ok) {
        const data = await res.json();
        this.recipesList = data.recipes || [];
        this.renderRecipesGrid();
        this.updateRecipesUserContext();
      }
    } catch (err) {
      console.error('Load recipes error:', err);
    }
  },

  updateRecipesUserContext() {
    const userNameEl = document.getElementById('recipes-user-name');
    const userGoalEl = document.getElementById('recipes-user-goal');

    if (this.userProfile) {
      if (userNameEl) userNameEl.textContent = this.userProfile.name;
      if (userGoalEl) {
        const goalStr = this.userProfile.fitness_objective.replace('_', ' ');
        const dietStr = this.userProfile.dietary_preference;
        userGoalEl.textContent = `Goal: ${goalStr} • ${dietStr}`;
      }
    }
  },

  renderRecipesGrid() {
    const container = document.getElementById('recipes-grid');
    const emptyState = document.getElementById('recipes-empty-state');
    const countBadge = document.getElementById('recipes-count-badge');

    if (!container) return;

    // Filter recipes based on current category and search query
    let filtered = this.recipesList.filter(r => {
      // Category filtering
      if (this.selectedRecipeCategory !== 'all') {
        if (this.selectedRecipeCategory === 'recommended') {
          if (!r.is_recommended) return false;
        } else if (!r.categories || !r.categories.includes(this.selectedRecipeCategory)) {
          return false;
        }
      }

      // Search query filtering
      if (this.recipeSearchQuery) {
        const q = this.recipeSearchQuery;
        const nameMatch = r.name.toLowerCase().includes(q);
        const hindiMatch = (r.hindi_name || '').toLowerCase().includes(q);
        const descMatch = r.description.toLowerCase().includes(q);
        const catMatch = (r.categories || []).some(c => c.toLowerCase().includes(q));
        const ingMatch = (r.ingredients || []).some(i => i.ingredient_name.toLowerCase().includes(q));

        if (!nameMatch && !hindiMatch && !descMatch && !catMatch && !ingMatch) {
          return false;
        }
      }

      return true;
    });

    if (countBadge) {
      countBadge.textContent = `Showing ${filtered.length} of ${this.recipesList.length} recipes`;
    }

    if (filtered.length === 0) {
      container.innerHTML = '';
      if (emptyState) emptyState.classList.remove('hidden');
      return;
    }

    if (emptyState) emptyState.classList.add('hidden');

    container.innerHTML = filtered.map(r => {
      const imgUrl = r.image || '/static/assets/images/thali_meal.jpg';
      const diffBadgeClass = r.difficulty === 'Easy' ? 'difficulty-badge-easy' : (r.difficulty === 'Medium' ? 'difficulty-badge-medium' : 'difficulty-badge-hard');
      const dietBadgeClass = r.dietary_type === 'vegetarian' ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30' : (r.dietary_type === 'non-vegetarian' ? 'bg-rose-500/20 text-rose-300 border-rose-500/30' : 'bg-amber-500/20 text-amber-300 border-amber-500/30');

      return `
        <div onclick="app.openRecipeDetail('${r.id}')" class="glass-card-interactive group flex flex-col justify-between">
          
          <!-- Image Wrapper with Badges -->
          <div class="food-card-img-wrapper">
            <img src="${imgUrl}" alt="${r.name}" class="food-card-img">
            <div class="food-card-img-overlay"></div>
            
            <!-- Top Badges -->
            <div class="absolute top-3 left-3 right-3 flex items-center justify-between gap-2">
              <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase border ${dietBadgeClass} backdrop-blur-md">
                ${r.dietary_type}
              </span>
              
              <div class="flex items-center gap-1.5">
                ${r.is_recommended ? `
                  <span class="px-2 py-0.5 rounded-full text-[10px] font-bold uppercase bg-indigo-500/90 text-white border border-indigo-300 shadow-md backdrop-blur-md flex items-center gap-1">
                    <i data-lucide="sparkles" class="w-3 h-3"></i> Recommended
                  </span>
                ` : ''}
                <span class="px-2 py-0.5 rounded-full text-[10px] font-bold uppercase border ${diffBadgeClass} backdrop-blur-md">
                  ${r.difficulty}
                </span>
              </div>
            </div>

            <!-- Bottom Title on Image -->
            <div class="absolute bottom-3 left-3 right-3">
              <h4 class="text-base font-bold text-white font-['Outfit'] group-hover:text-[#00d084] transition line-clamp-1">${r.name}</h4>
              ${r.hindi_name ? `<p class="text-[11px] text-gray-300 font-medium">${r.hindi_name}</p>` : ''}
            </div>
          </div>

          <!-- Card Content Body -->
          <div class="p-5 space-y-4">
            <p class="text-xs text-gray-400 line-clamp-2 leading-relaxed">${r.description}</p>
            
            <!-- 4 Macro Pills Grid -->
            <div class="grid grid-cols-4 gap-1.5 text-center">
              <div class="recipe-card-stat">
                <span class="text-[10px] text-gray-400 block font-medium">Energy</span>
                <span class="text-xs font-bold text-white font-['Outfit']">${Math.round(r.calories)}</span>
                <span class="text-[9px] text-gray-500">kcal</span>
              </div>
              <div class="recipe-card-stat border-[#f43f5e]/25">
                <span class="text-[10px] text-[#f43f5e] block font-medium">Protein</span>
                <span class="text-xs font-bold text-[#f43f5e] font-['Outfit']">${Math.round(r.protein * 10) / 10}g</span>
                <span class="text-[9px] text-gray-500">prot</span>
              </div>
              <div class="recipe-card-stat border-[#ff6b35]/25">
                <span class="text-[10px] text-[#ff6b35] block font-medium">Carbs</span>
                <span class="text-xs font-bold text-[#ff6b35] font-['Outfit']">${Math.round(r.carbohydrates * 10) / 10}g</span>
                <span class="text-[9px] text-gray-500">carbs</span>
              </div>
              <div class="recipe-card-stat border-yellow-400/25">
                <span class="text-[10px] text-yellow-400 block font-medium">Fat</span>
                <span class="text-xs font-bold text-yellow-400 font-['Outfit']">${Math.round(r.fat * 10) / 10}g</span>
                <span class="text-[9px] text-gray-500">fats</span>
              </div>
            </div>

            <!-- Meta Times & Action Footer -->
            <div class="pt-3 border-t border-white/5 flex items-center justify-between text-xs">
              <div class="flex items-center gap-3 text-gray-400 text-[11px]">
                <span class="flex items-center gap-1">
                  <i data-lucide="clock" class="w-3.5 h-3.5 text-[#00d084]"></i> ${r.preparation_time}
                </span>
                <span class="flex items-center gap-1">
                  <i data-lucide="flame" class="w-3.5 h-3.5 text-[#ff6b35]"></i> ${r.cooking_time}
                </span>
              </div>
              
              <span class="text-[#00d084] font-bold text-xs flex items-center gap-1 group-hover:translate-x-1 transition">
                View Recipe &rarr;
              </span>
            </div>

          </div>

        </div>
      `;
    }).join('');

    this.refreshIcons();
  },

  filterRecipesByCategory(category) {
    this.selectedRecipeCategory = category;

    // Update chip active classes
    const chips = document.querySelectorAll('#recipe-category-chips .category-chip');
    chips.forEach(chip => {
      if (chip.getAttribute('data-cat') === category) {
        chip.classList.add('active');
        if (category === 'recommended') {
          chip.classList.add('active-recommended');
        }
      } else {
        chip.classList.remove('active', 'active-recommended');
      }
    });

    this.renderRecipesGrid();
  },

  handleRecipeSearch(query) {
    this.recipeSearchQuery = (query || '').trim().toLowerCase();
    const clearBtn = document.getElementById('recipe-search-clear');
    if (clearBtn) {
      if (this.recipeSearchQuery) {
        clearBtn.classList.remove('hidden');
      } else {
        clearBtn.classList.add('hidden');
      }
    }
    this.renderRecipesGrid();
  },

  clearRecipeSearch() {
    const input = document.getElementById('recipe-search-input');
    const clearBtn = document.getElementById('recipe-search-clear');
    if (input) input.value = '';
    if (clearBtn) clearBtn.classList.add('hidden');
    this.recipeSearchQuery = '';
    this.renderRecipesGrid();
  },

  resetRecipeFilters() {
    this.clearRecipeSearch();
    this.filterRecipesByCategory('all');
  },

  openRecipeDetail(recipeId) {
    const recipe = this.recipesList.find(r => r.id === recipeId);
    if (!recipe) return;

    this.currentRecipeDetail = recipe;

    // Header & Meta
    const imgEl = document.getElementById('modal-recipe-img');
    const titleEl = document.getElementById('modal-recipe-title');
    const hindiEl = document.getElementById('modal-recipe-hindi');
    const descEl = document.getElementById('modal-recipe-desc');
    const dietBadge = document.getElementById('modal-recipe-diet-badge');
    const diffBadge = document.getElementById('modal-recipe-diff-badge');
    const recBadge = document.getElementById('modal-recipe-recommended-badge');
    const prepEl = document.getElementById('modal-recipe-prep');
    const cookEl = document.getElementById('modal-recipe-cook');
    const servEl = document.getElementById('modal-recipe-servings');
    const diffText = document.getElementById('modal-recipe-difficulty-text');

    if (imgEl) imgEl.src = recipe.image || '/static/assets/images/thali_meal.jpg';
    if (titleEl) titleEl.textContent = recipe.name;
    if (hindiEl) hindiEl.textContent = recipe.hindi_name || '';
    if (descEl) descEl.textContent = recipe.description;

    if (dietBadge) {
      dietBadge.textContent = recipe.dietary_type;
      dietBadge.className = recipe.dietary_type === 'vegetarian' ? 'px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : (recipe.dietary_type === 'non-vegetarian' ? 'px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase bg-rose-500/20 text-rose-300 border border-rose-500/30' : 'px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase bg-amber-500/20 text-amber-300 border border-amber-500/30');
    }

    if (diffBadge) {
      diffBadge.textContent = recipe.difficulty;
      diffBadge.className = recipe.difficulty === 'Easy' ? 'px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase difficulty-badge-easy' : (recipe.difficulty === 'Medium' ? 'px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase difficulty-badge-medium' : 'px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase difficulty-badge-hard');
    }

    if (recBadge) {
      if (recipe.is_recommended) {
        recBadge.classList.remove('hidden');
      } else {
        recBadge.classList.add('hidden');
      }
    }

    if (prepEl) prepEl.textContent = recipe.preparation_time;
    if (cookEl) cookEl.textContent = recipe.cooking_time;
    if (servEl) servEl.textContent = `${recipe.servings} serving${recipe.servings === 1 ? '' : 's'}`;
    if (diffText) diffText.textContent = recipe.difficulty;

    // Smart Nutrition 5 Macro Cards
    const calEl = document.getElementById('modal-macro-cal');
    const protEl = document.getElementById('modal-macro-prot');
    const carbsEl = document.getElementById('modal-macro-carbs');
    const fatEl = document.getElementById('modal-macro-fat');
    const fiberEl = document.getElementById('modal-macro-fiber');

    if (calEl) calEl.textContent = Math.round(recipe.calories);
    if (protEl) protEl.textContent = `${recipe.protein}g`;
    if (carbsEl) carbsEl.textContent = `${recipe.carbohydrates}g`;
    if (fatEl) fatEl.textContent = `${recipe.fat}g`;
    if (fiberEl) fiberEl.textContent = `${recipe.fiber}g`;

    // Exact Ingredients List Grid
    const ingCount = document.getElementById('modal-ingredients-count');
    const ingGrid = document.getElementById('modal-ingredients-grid');

    if (ingCount) ingCount.textContent = `${recipe.ingredients.length} ingredients`;
    if (ingGrid) {
      ingGrid.innerHTML = recipe.ingredients.map(ing => `
        <div class="p-3 rounded-xl bg-slate-900/90 border border-white/10 flex items-start justify-between gap-3 text-xs hover:border-white/20 transition">
          <div class="space-y-0.5">
            <span class="font-bold text-white block">${ing.ingredient_name}</span>
            ${ing.notes ? `<span class="text-[10px] text-gray-400 block italic">${ing.notes}</span>` : ''}
            <span class="text-[10px] text-gray-500 block">
              ${Math.round(ing.calories)} kcal &bull; <span class="text-[#f43f5e] font-semibold">${ing.protein}g P</span>
            </span>
          </div>

          <div class="px-2.5 py-1 rounded-lg bg-slate-950 border border-white/10 font-mono text-emerald-400 font-bold text-xs whitespace-nowrap">
            ${ing.quantity} ${ing.unit}
          </div>
        </div>
      `).join('');
    }

    // Ingredient-Level Nutrition Breakdown Table
    const tbody = document.getElementById('modal-breakdown-tbody');
    if (tbody) {
      const rowsHtml = recipe.ingredients.map(ing => `
        <tr class="ingredient-table-row">
          <td class="py-2 px-3 font-medium text-white">${ing.ingredient_name}</td>
          <td class="py-2 px-3 text-right font-mono text-emerald-400">${ing.quantity} ${ing.unit}</td>
          <td class="py-2 px-3 text-right font-mono">${Math.round(ing.calories)}</td>
          <td class="py-2 px-3 text-right font-mono text-[#f43f5e]">${ing.protein}g</td>
          <td class="py-2 px-3 text-right font-mono text-[#ff6b35]">${ing.carbohydrates}g</td>
          <td class="py-2 px-3 text-right font-mono text-yellow-400">${ing.fat}g</td>
          <td class="py-2 px-3 text-right font-mono text-[#00d084]">${ing.fiber}g</td>
        </tr>
      `).join('');

      const totalRowHtml = `
        <tr class="bg-slate-900/90 font-bold text-white border-t border-white/15">
          <td class="py-2.5 px-3">Total Nutrition per Serving</td>
          <td class="py-2.5 px-3 text-right font-mono text-[#00d084]">1 Serving</td>
          <td class="py-2.5 px-3 text-right font-mono">${Math.round(recipe.calories)} kcal</td>
          <td class="py-2.5 px-3 text-right font-mono text-[#f43f5e]">${recipe.protein}g</td>
          <td class="py-2.5 px-3 text-right font-mono text-[#ff6b35]">${recipe.carbohydrates}g</td>
          <td class="py-2.5 px-3 text-right font-mono text-yellow-400">${recipe.fat}g</td>
          <td class="py-2.5 px-3 text-right font-mono text-[#00d084]">${recipe.fiber}g</td>
        </tr>
      `;

      tbody.innerHTML = rowsHtml + totalRowHtml;
    }

    // Step-by-Step Cooking Instructions
    const stepsList = document.getElementById('modal-instructions-list');
    if (stepsList) {
      stepsList.innerHTML = recipe.instructions.map((step, idx) => `
        <div class="p-3.5 rounded-xl bg-slate-900/80 border border-white/10 flex items-start gap-3 text-xs leading-relaxed text-gray-200">
          <span class="step-number-bubble">${idx + 1}</span>
          <p class="pt-0.5">${step}</p>
        </div>
      `).join('');
    }

    // Context Engine Button
    const contextBtn = document.getElementById('modal-analyze-in-context-btn');
    if (contextBtn) {
      contextBtn.onclick = () => this.analyzeRecipeInContextEngine(recipe.id);
    }

    // Show Modal
    const modal = document.getElementById('recipe-detail-modal');
    if (modal) {
      modal.classList.remove('hidden');
      modal.classList.add('flex');
    }

    this.refreshIcons();
  },

  closeRecipeDetail() {
    const modal = document.getElementById('recipe-detail-modal');
    if (modal) {
      modal.classList.remove('flex');
      modal.classList.add('hidden');
    }
  },

  async analyzeRecipeInContextEngine(recipeId) {
    const recipe = this.recipesList.find(r => r.id === recipeId);
    if (!recipe) return;

    this.closeRecipeDetail();

    // Map ingredients to detected food items for scanner & Personal Context Engine
    this.currentDetectedItems = recipe.ingredients.map(ing => {
      // Find food in catalog if available for portion options
      const foodMatch = this.foodCatalog.find(f => 
        f.name.toLowerCase().includes(ing.ingredient_name.toLowerCase()) || 
        ing.ingredient_name.toLowerCase().includes(f.name.toLowerCase())
      );

      return {
        food_id: foodMatch ? foodMatch.id : `recipe_${ing.ingredient_name.toLowerCase().replace(/[^a-z0-9]/g, '_')}`,
        name: ing.ingredient_name,
        hindi_name: null,
        confidence: 1.0,
        portion_size: 'custom',
        portion_grams: ing.quantity,
        calories: ing.calories,
        protein: ing.protein,
        carbs: ing.carbohydrates,
        fat: ing.fat,
        fiber: ing.fiber,
        user_confirmed: true
      };
    });

    this.currentMealTitle = recipe.name;
    this.currentMealImageUrl = recipe.image || '/static/assets/images/thali_meal.jpg';
    this.currentMealBoxes = [];

    // Navigate to scanner, update UI, and execute Context Engine analysis
    this.navigate('scanner');
    this.renderDetectionStage();
    this.renderDetectedItems();
    this.showPreviewState(this.currentMealImageUrl, recipe.name);

    this.showToast(`Imported ${recipe.name} into Context Engine!`);

    // Execute Personal Context Engine
    await this.executeMealAnalysis();
  }
};

// Initialize App on DOM Ready
document.addEventListener('DOMContentLoaded', () => {
  app.init();
});

