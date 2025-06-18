'use strict';

document.addEventListener('DOMContentLoaded', function () {
  const formDelete = document.querySelector('#formDelete');
  const deleteButton = formDelete?.querySelector('.delete-button');
  const objectDeletion = formDelete?.querySelector('#objectDeletion');
  const objectType = formDelete.dataset.object || 'this item';
  const objectName = formDelete.dataset.name || 'this item';

  if (formDelete && deleteButton && objectDeletion) {
    // Enable/disable delete button based on checkbox
    objectDeletion.addEventListener('change', function () {
      deleteButton.disabled = !this.checked;
    });

    // SweetAlert confirmation
    deleteButton.addEventListener('click', function (e) {
      e.preventDefault(); // Prevent form submission

      if (!objectDeletion.checked) {
        Swal.fire({
          title: 'Confirmation Required',
          text: 'Please check the confirmation checkbox to proceed.',
          icon: 'warning',
          customClass: {
            confirmButton: 'btn btn-success waves-effect waves-light'
          }
        });
        return;
      }

      Swal.fire({
        title: `Delete ${objectType}?`,
        text: `Are you sure you want to delete the ${objectType.toLowerCase()} - ${objectName}?`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Yes, delete it!',
        cancelButtonText: 'Cancel',
        customClass: {
          confirmButton: 'btn btn-danger me-2 waves-effect waves-light',
          cancelButton: 'btn btn-label-secondary waves-effect waves-light'
        },
        buttonsStyling: false
      }).then((result) => {
        if (result.isConfirmed) {
          formDelete.submit();
        }
      });
    });
  }
});