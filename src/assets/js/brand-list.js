'use strict';

$(function () {
  let borderColor, bodyBg, headingColor;

  if (isDarkStyle) {
    borderColor = config.colors_dark.borderColor;
    bodyBg = config.colors_dark.bodyBg;
    headingColor = config.colors_dark.headingColor;
  } else {
    borderColor = config.colors.borderColor;
    bodyBg = config.colors.bodyBg;
    headingColor = config.colors.headingColor;
  }

  const dt_table = $('.datatables-brand-list'),
    brandAdd = '/brands/add/';

  if (dt_table.length) {
    dt_table.DataTable({
      ajax: '/api/brands/',
      columns: [
        { data: 'control' }, // Control column
        { data: 'name' }, // Use 'name' as the data key, render handles logo combination
        { data: 'description' },
        { data: 'actions' } // Actions column
      ],
      columnDefs: [
        {
          className: 'control',
          searchable: false,
          orderable: false,
          targets: 0,
          render: () => ''
        },
        {
          targets: 1,
          responsivePriority: 1,
          render: function (data, type, full, meta) {
            var $name = full['name'],
              $id = full['id'],
              $image = full['logo'];
            var $output = $image
              ? '<img src="' + $image + '" alt="Brand-' + $id + '" class="rounded-2" style="width: 40px; height: 40px;">'
              : '<span class="avatar-initial rounded-2 bg-label-secondary">' + ($name ? $name.charAt(0).toUpperCase() : 'N') + '</span>';
            return (
              '<div class="d-flex justify-content-start align-items-center category-name">' +
              '<div class="avatar-wrapper">' +
              '<div class="avatar avatar me-4 rounded-2 bg-label-secondary">' +
              $output +
              '</div>' +
              '</div>' +
              '<div class="d-flex flex-column">' +
              '<h6 class="text-nowrap mb-0">' + ($name || 'N/A') + '</h6>' +
              '</div>' +
              '</div>'
            );
          }
        },
        {
          targets: 2,
          render: (data, type, full) => full.description || 'N/A'
        },
        {
          targets: -1,
          title: 'Actions',
          searchable: false,
          orderable: false,
          render: function (data, type, full, meta) {
            return (
              '<div class="d-inline-block text-nowrap">' +
              '<a href="/brands/update/' + full['id'] + '/" class="btn btn-sm btn-icon btn-text-secondary rounded-pill waves-effect waves-light"><i class="ti ti-edit ti-md"></i></a>' +
              '</div>'
            );
          }
        }
      ],
      order: [[1, 'asc']], // Sort by name
      dom:
        '<"card-header d-flex border-top rounded-0 flex-wrap py-0 flex-column flex-md-row align-items-start"' +
        '<"me-5 ms-n4 pe-5 mb-n6 mb-md-0"f>' +
        '<"d-flex justify-content-start justify-content-md-end align-items-baseline"<"dt-action-buttons d-flex flex-column align-items-start align-items-sm-center justify-content-sm-center pt-0 gap-sm-4 gap-sm-0 flex-sm-row"lB>>' +
        '>t' +
        '<"row"' +
        '<"col-sm-12 col-md-6"i>' +
        '<"col-sm-12 col-md-6"p>' +
        '>',
      buttons: [
        {
          extend: 'collection',
          className: 'btn btn-label-secondary dropdown-toggle me-4 waves-effect waves-light',
          text: '<i class="ti ti-upload me-1 ti-xs"></i>Export',
          buttons: ['print', 'csv', 'excel', 'pdf', 'copy']
        },
        {
          text: '<i class="ti ti-plus me-0 me-sm-1 ti-xs"></i><span class="d-none d-sm-inline-block">Add Brand</span>',
          className: 'add-new btn btn-primary ms-2 ms-sm-0 waves-effect waves-light',
          action: () => {
            window.location.href = brandAdd;
          }
        }
      ],
      language: {
        sLengthMenu: '_MENU_',
        search: '',
        searchPlaceholder: 'Search Brand',
        info: 'Displaying _START_ to _END_ of _TOTAL_ entries',
        paginate: {
          next: '<i class="ti ti-chevron-right ti-sm"></i>',
          previous: '<i class="ti ti-chevron-left ti-sm"></i>'
        }
      },
      responsive: true
    });

    // Cleanup small inputs
    setTimeout(() => {
      $('.dataTables_filter .form-control').removeClass('form-control-sm');
      $('.dataTables_length .form-select').removeClass('form-select-sm');
    }, 300);
  }
});