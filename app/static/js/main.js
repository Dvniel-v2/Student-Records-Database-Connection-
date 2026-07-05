document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('record-form');
  const status = document.getElementById('form-status');

  if (!form || !status) {
    return;
  }

  form.addEventListener('submit', () => {
    status.textContent = 'Saving your record...';
  });
});
