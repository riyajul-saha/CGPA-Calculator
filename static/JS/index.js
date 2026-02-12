(function () {
  "use strict";

  // ----- DOM elements -----
  const sgpa1Input = document.getElementById('sgpa1');
  const sgpa2Input = document.getElementById('sgpa2');
  const credit1Input = document.getElementById('credit1');
  const credit2Input = document.getElementById('credit2');
  const error1 = document.getElementById('sgpa1Error');
  const error2 = document.getElementById('sgpa2Error');
  const cgpaDisplay = document.getElementById('cgpaDisplay');
  const calcBtn = document.getElementById('calculateSaveBtn');
  const studentNameInput = document.getElementById('studentName');
  const rollInput = document.getElementById('roll');
  const studentNumberInput = document.getElementById('studentNumber');
  const semesterSelect = document.getElementById('semesterSelect');

  // ----- helper: validate single SGPA (>10 shows red message) -----
  function validateSGPA(value, errorElement) {
    // if field is empty -> no error (we show nothing, but later we treat as not calculated)
    if (value === null || value === undefined || value.trim() === '') {
      errorElement.innerText = '';   // no error
      return true;   // empty considered valid for message? We'll handle in calculation
    }
    const num = parseFloat(value);
    if (isNaN(num)) {
      errorElement.innerText = 'Enter a valid number';
      return false;
    }
    if (num > 10) {
      errorElement.innerText = 'SGPA must be ≤ 10.00';   // RED ERROR MESSAGE exactly as required
      return false;
    }
    if (num < 0) {
      errorElement.innerText = 'SGPA cannot be negative';
      return false;
    }
    // valid
    errorElement.innerText = '';
    return true;
  }

  // ----- realtime validation on input (for both SGPA fields) -----
  if (sgpa1Input) {
    sgpa1Input.addEventListener('input', function (e) {
      validateSGPA(e.target.value, error1);
    });
  }

  if (sgpa2Input) {
    sgpa2Input.addEventListener('input', function (e) {
      validateSGPA(e.target.value, error2);
    });
  }

  // ----- also validate on blur (extra touch) -----
  if (sgpa1Input) {
    sgpa1Input.addEventListener('blur', function (e) {
      validateSGPA(e.target.value, error1);
    });
  }
  if (sgpa2Input) {
    sgpa2Input.addEventListener('blur', function (e) {
      validateSGPA(e.target.value, error2);
    });
  }

  // ----- Calculate & Save button action -----
  async function calculateCGPA() {
    // 1. get trimmed values
    const val1 = sgpa1Input.value.trim();
    const val2 = sgpa2Input.value.trim();

    // 2. validate both fields (show errors if >10)
    const isValid1 = validateSGPA(val1, error1);
    const isValid2 = validateSGPA(val2, error2);

    // 3. if either field is empty OR invalid ( >10 or not number ) → show proper message and fallback
    const num1 = parseFloat(val1);
    const num2 = parseFloat(val2);

    // check for empty
    if (val1 === '' || val2 === '') {
      cgpaDisplay.innerText = '--';
      return;
    }

    // if either is NaN or invalid per validation (isValid1/isValid2 false)
    if (!isValid1 || !isValid2 || isNaN(num1) || isNaN(num2)) {
      cgpaDisplay.innerText = '?';
      return;
    }

    // Get credit values
    let c1 = parseFloat(credit1Input.value);
    let c2 = parseFloat(credit2Input.value);

    // Default handles in backend, but good to send what we have
    if (isNaN(c1)) c1 = 1;
    if (isNaN(c2)) c2 = 1;

    // Send to backend
    try {
      // Clear previous messages
      const successDiv = document.getElementById('successMessage');
      if (successDiv) successDiv.innerText = '';

      const response = await fetch('/calculate_cgpa', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          sgpa1: num1,
          sgpa2: num2,
          credit1: c1,
          credit2: c2,
          name: studentNameInput ? studentNameInput.value.trim() : '',
          roll: rollInput ? rollInput.value.trim() : '',
          number: studentNumberInput ? studentNumberInput.value.trim() : '',
          semester: semesterSelect ? semesterSelect.value : ''
        })
      });

      const data = await response.json();

      if (response.ok) {
        cgpaDisplay.innerText = data.cgpa;
        // Show success message if present
        if (data.message && successDiv) {
          successDiv.innerText = data.message;
          // Optional: clear after 5 seconds
          setTimeout(() => { successDiv.innerText = ''; }, 5000);
        }
      } else {
        console.error('Error:', data.error);
        cgpaDisplay.innerText = 'Err';
        if (successDiv) {
             successDiv.style.color = 'red';
             successDiv.innerText = 'Error saving data';
        }
      }
    } catch (error) {
      console.error('Fetch error:', error);
      cgpaDisplay.innerText = 'Err';
    }
  }

  // button click event
  if (calcBtn) {
    calcBtn.addEventListener('click', function (e) {
      e.preventDefault();
      calculateCGPA();
      // you can also simulate "save" – here we just show an subtle alert/design feedback
      // (extra touch: blink button)
      calcBtn.style.background = '#1e40af';
      setTimeout(() => { calcBtn.style.background = '#2563eb'; }, 120);
    });
  }

  // initialize: set default roll explicitly (already in html value) 
  // also trigger validation on page load if prefilled? we can clear errors.
  window.addEventListener('DOMContentLoaded', function () {
    // default roll visible, but also validate empty sgpa fields (no error)
    if (sgpa1Input) validateSGPA(sgpa1Input.value, error1);
    if (sgpa2Input) validateSGPA(sgpa2Input.value, error2);
    // optional: prefill sample numbers? no, keep empty for user.
  });

  // mobile friendly: ensure numeric keyboard for SGPA
  // (already step=0.01)

  // ----- Dynamic Label Update logic -----
  // semesterSelect already defined at top

  const label1 = document.getElementById('sgpa1Label');
  const label2 = document.getElementById('sgpa2Label');

  function updateSGPALabels() {
    const currentSem = parseInt(semesterSelect.value, 10);
    if (isNaN(currentSem)) return;

    // Logic: Input 1 = Current - 2, Input 2 = Current - 1
    const prev1 = currentSem - 2;
    const prev2 = currentSem - 1;

    if (label1) label1.textContent = `SGPA (Semester-${prev1})`;
    if (label2) label2.textContent = `SGPA (Semester-${prev2})`;

    const creditLabel1 = document.getElementById('credit1Label');
    const creditLabel2 = document.getElementById('credit2Label');
    const credit1Input = document.getElementById('credit1');
    const credit2Input = document.getElementById('credit2');

    if (creditLabel1) creditLabel1.textContent = `Credit (Semester-${prev1})`;
    if (creditLabel2) creditLabel2.textContent = `Credit (Semester-${prev2})`;

    // Default values for Semester 3
    if (currentSem === 3) {
      if (credit1Input) credit1Input.value = 20;
      if (credit2Input) credit2Input.value = 24;
    }
  }

  if (semesterSelect) {
    semesterSelect.addEventListener('change', updateSGPALabels);
    // Initialize on load
    updateSGPALabels();
  }
})();
