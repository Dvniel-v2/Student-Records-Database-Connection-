document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('student-form');
  const status = document.getElementById('form-status');

  if (!form || !status) {
    return;
  }

  form.addEventListener('submit', () => {
    status.textContent = 'Saving student record...';
  });
});
