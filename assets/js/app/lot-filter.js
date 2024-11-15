//const form = document.querySelector('#search-form');
//const subBeginGreater = document.querySelector('#sub-bg-input');
//const subBeginLower   = document.querySelector('#sub-bl-input');
//const subEndGreater = document.querySelector('#sub-eg-input');
//const subEndLower   = document.querySelector('#sub-el-input');
//const bidBeginGreater = document.querySelector('#bid-bg-input');
//const bidBeginLower   = document.querySelector('#bid-bl-input');
//
//const subBeginPicker = flatpickr('#sub-begin-input', {
//    locale:'ru',
//    dateFormat:'d.m.Y',
//    mode:'range',
//    defaultDate: [subBeginGreater.value, subBeginLower.value]
//});
//
//const subEndPicker = flatpickr('#sub-end-input', {
//    locale:'ru',
//    dateFormat:'d.m.Y',
//    mode:'range',
//    defaultDate: [subEndGreater.value, subEndLower.value]
//});
//
//const bidBeginPicker = flatpickr('#bid-begin-input', {
//    locale:'ru',
//    dateFormat:'d.m.Y',
//    mode:'range',
//    defaultDate: [bidBeginGreater.value, bidBeginLower.value]
//});
//
//document.querySelector('#submit-button').addEventListener('click', function(e) {
//    if (subBeginPicker.selectedDates.length) {
//        subBeginGreater.value = subBeginPicker.selectedDates[0].toLocaleDateString("ru-RU");
//        subBeginLower.value   = subBeginPicker.selectedDates[1].toLocaleDateString("ru-RU");
//    }
//    if (subEndPicker.selectedDates.length) {
//        subEndGreater.value = subEndPicker.selectedDates[0].toLocaleDateString("ru-RU");
//        subEndLower.value   = subEndPicker.selectedDates[1].toLocaleDateString("ru-RU");
//    }
//    if (bidBeginPicker.selectedDates.length) {
//        bidBeginGreater.value = bidBeginPicker.selectedDates[0].toLocaleDateString("ru-RU");
//        bidBeginLower.value   = bidBeginPicker.selectedDates[1].toLocaleDateString("ru-RU");
//    }
//    form.submit();
//});
//
//document.querySelector('#reset-button').addEventListener('click', function(e) {
//    document.querySelector('#name-input').value    = '';
//    document.querySelector('#number-input').value  = '';
//    document.querySelector('#sum-input').value     = '';
//    document.querySelector('#company-input').value = '';
//    document.querySelector('#client-input').value  = '';
//    subBeginGreater.value = '';
//    subBeginLower.value   = '';
//    subEndGreater.value   = '';
//    subEndLower.value     = '';
//    bidBeginGreater.value = '';
//    bidBeginLower.value   = '';
//    document.querySelector('#status-select').selectedIndex = 0;
//    document.querySelector('#eoz-select').selectedIndex = 0;
//    form.submit();
//});


const form = document.querySelector('#search-form');
const searchInput = document.querySelector('#search-input');
const companyInput = document.querySelector('#company-input');
const clientInput = document.querySelector('#client-input');
const bidBeginInput = document.querySelector('#bid-begin-input');
const subBeginInput = document.querySelector('#sub-begin-input');
const subEndInput = document.querySelector('#sub-end-input');
const statusSelect = document.querySelector('#status-select');

searchInput.addEventListener('change', updateFormAndSubmit);
companyInput.addEventListener('change', updateFormAndSubmit);
clientInput.addEventListener('change', updateFormAndSubmit);
bidBeginInput.addEventListener('change', updateFormAndSubmit);
subBeginInput.addEventListener('change', updateFormAndSubmit);
subEndInput.addEventListener('change', updateFormAndSubmit);
statusSelect.addEventListener('change', updateFormAndSubmit);

function updateFormAndSubmit() {
    const searchValue = searchInput.value;
    const companyValue = companyInput.value;
    const clientValue = clientInput.value;
    const bidBeginValue = bidBeginInput.value;
    const subBeginValue = subBeginInput.value;
    const subEndValue = subEndInput.value;
    const statusValue = statusSelect.value;

    form.querySelector('[name="search"]').value = searchValue;
    form.querySelector('[name="company"]').value = companyValue;
    form.querySelector('[name="client"]').value = clientValue;
    form.querySelector('[name="bid_bg"]').value = bidBeginValue;
    form.querySelector('[name="sub_bg"]').value = subBeginValue;
    form.querySelector('[name="sub_eg"]').value = subEndValue;
    form.querySelector('[name="status"]').value = statusValue;

    form.submit();
}






