/**
 * App eCommerce Category List
 */
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

  // Variable declaration for table
  var dt_category_table = $('.datatables-category-list'),
    categoryAdd = '/categories/add/',
    statusObj = {
      true: { title: 'Hidden', class: 'bg-label-warning' },
      false: { title: 'Visible', class: 'bg-label-success' }
    };

  // E-commerce Categories datatable
  if (dt_category_table.length) {
    var dt_categories = dt_category_table.DataTable({
      ajax: '/api/categories/', // DRF API endpoint
      columns: [
        { data: '' }, // Control
        { data: 'id' }, // ID
        { data: 'name' }, // Name
        { data: 'display_name' }, // Display Name
        { data: 'type' }, // Type
        { data: 'department' }, // Department
        { data: 'parent' }, // Parent
        { data: 'total_products' }, // Total Products
        { data: 'hide' }, // Status (Hide)
        { data: '' } // Actions
      ],
      columnDefs: [
        {
          className: 'control',
          searchable: false,
          orderable: false,
          responsivePriority: 2,
          targets: 0,
          render: function (data, type, full, meta) {
            return '';
          }
        },
        {
          targets: 1,
          orderable: false,
          checkboxes: {
            selectAllRender: '<input type="checkbox" class="form-check-input">'
          },
          render: function () {
            return '<input type="checkbox" class="dt-checkboxes form-check-input">';
          },
          searchable: false
        },
        {
          targets: 2,
          responsivePriority: 1,
          render: function (data, type, full, meta) {
            var $name = full['name'],
              $id = full['id'],
              $image = full['image'];
            var $output = $image
              ? '<img src="' + $image + '" alt="Category-' + $id + '" class="rounded-2" style="width: 40px; height: 40px;">'
              : '<span class="avatar-initial rounded-2 bg-label-secondary">' + $name.charAt(0).toUpperCase() + '</span>';
            return (
              '<div class="d-flex justify-content-start align-items-center category-name">' +
              '<div class="avatar-wrapper">' +
              '<div class="avatar avatar me-4 rounded-2 bg-label-secondary">' +
              $output +
              '</div>' +
              '</div>' +
              '<div class="d-flex flex-column">' +
              '<h6 class="text-nowrap mb-0">' + $name + '</h6>' +
              '</div>' +
              '</div>'
            );
          }
        },
        {
          targets: 3,
          render: function (data, type, full, meta) {
            return full['display_name'] || 'N/A';
          }
        },
        {
          targets: 4,
          render: function (data, type, full, meta) {
            return full['type'] && full['type']['name'] ? full['type']['name'] : 'N/A';
          }
        },
        {
          targets: 5,
          render: function (data, type, full, meta) {
            return full['department'] && full['department']['name'] ? full['department']['name'] : 'N/A';
          }
        },
        {
          targets: 6,
          render: function (data, type, full, meta) {
            return full['parent'] && full['parent']['name'] ? full['parent']['name'] : 'None';
          }
        },
        {
          targets: 7,
          responsivePriority: 3,
          render: function (data, type, full, meta) {
            return '<span>' + full['total_products'] + '</span>';
          }
        },
        {
          targets: 8,
          render: function (data, type, full, meta) {
            var $hide = full['hide'];
            return (
              '<span class="badge ' + statusObj[$hide].class + '" text-capitalized>' +
              statusObj[$hide].title +
              '</span>'
            );
          }
        },
        {
          targets: -1,
          title: 'Actions',
          searchable: false,
          orderable: false,
          render: function (data, type, full, meta) {
            return (
              '<div class="d-inline-block text-nowrap">' +
              '<a href="/categories/update/' + full['id'] + '/" class="btn btn-sm btn-icon btn-text-secondary rounded-pill waves-effect waves-light"><i class="ti ti-edit ti-md"></i></a>' +
              '</div>'
            );
          }
        }
      ],
      order: [2, 'asc'],
      dom:
        '<"card-header d-flex border-top rounded-0 flex-wrap py-0 flex-column flex-md-row align-items-start"' +
        '<"me-5 ms-n4 pe-5 mb-n6 mb-md-0"f>' +
        '<"d-flex justify-content-start justify-content-md-end align-items-baseline"<"dt-action-buttons d-flex flex-column align-items-start align-items-sm-center justify-content-sm-center pt-0 gap-sm-4 gap-sm-0 flex-sm-row"lB>>' +
        '>t' +
        '<"row"' +
        '<"col-sm-12 col-md-6"i>' +
        '<"col-sm-12 col-md-6"p>' +
        '>',
      lengthMenu: [7, 10, 20, 50, 70, 100],
      language: {
        sLengthMenu: '_MENU_',
        search: '',
        searchPlaceholder: 'Search Category',
        info: 'Displaying _START_ to _END_ of _TOTAL_ entries',
        paginate: {
          next: '<i class="ti ti-chevron-right ti-sm"></i>',
          previous: '<i class="ti ti-chevron-left ti-sm"></i>'
        }
      },
      buttons: [
        {
          extend: 'collection',
          className: 'btn btn-label-secondary dropdown-toggle me-4 waves-effect waves-light',
          text: '<i class="ti ti-upload me-1 ti-xs"></i>Export',
          buttons: [
            {
              extend: 'print',
              text: '<i class="ti ti-printer me-2"></i>Print',
              className: 'dropdown-item',
              exportOptions: {
                columns: [1, 2, 3, 4, 5, 6, 7, 8],
                format: {
                  body: function (inner, coldex, rowdex) {
                    if (inner.length <= 0) return inner;
                    var el = $.parseHTML(inner);
                    var result = '';
                    $.each(el, function (index, item) {
                      if (item.classList !== undefined && item.classList.contains('category-name')) {
                        result = result + item.lastChild.firstChild.textContent;
                      } else if (item.innerText === undefined) {
                        result = result + item.textContent;
                      } else result = result + item.innerText;
                    });
                    return result;
                  }
                }
              },
              customize: function (win) {
                $(win.document.body)
                  .css('color', headingColor)
                  .css('border-color', borderColor)
                  .css('background-color', bodyBg);
                $(win.document.body)
                  .find('table')
                  .addClass('compact')
                  .css('color', 'inherit')
                  .css('border-color', 'inherit')
                  .css('background-color', 'inherit');
              }
            },
            {
              extend: 'csv',
              text: '<i class="ti ti-file me-2"></i>Csv',
              className: 'dropdown-item',
              exportOptions: {
                columns: [1, 2, 3, 4, 5, 6, 7, 8],
                format: {
                  body: function (inner, coldex, rowdex) {
                    if (inner.length <= 0) return inner;
                    var el = $.parseHTML(inner);
                    var result = '';
                    $.each(el, function (index, item) {
                      if (item.classList !== undefined && item.classList.contains('category-name')) {
                        result = result + item.lastChild.firstChild.textContent;
                      } else if (item.innerText === undefined) {
                        result = result + item.textContent;
                      } else result = result + item.innerText;
                    });
                    return result;
                  }
                }
              }
            },
            {
              extend: 'excel',
              text: '<i class="ti ti-file-export me-2"></i>Excel',
              className: 'dropdown-item',
              exportOptions: {
                columns: [1, 2, 3, 4, 5, 6, 7, 8],
                format: {
                  body: function (inner, coldex, rowdex) {
                    if (inner.length <= 0) return inner;
                    var el = $.parseHTML(inner);
                    var result = '';
                    $.each(el, function (index, item) {
                      if (item.classList !== undefined && item.classList.contains('category-name')) {
                        result = result + item.lastChild.firstChild.textContent;
                      } else if (item.innerText === undefined) {
                        result = result + item.textContent;
                      } else result = result + item.innerText;
                    });
                    return result;
                  }
                }
              }
            },
            {
              extend: 'pdf',
              text: '<i class="ti ti-file-text me-2"></i>Pdf',
              className: 'dropdown-item',
              exportOptions: {
                columns: [1, 2, 3, 4, 5, 6, 7, 8],
                format: {
                  body: function (inner, coldex, rowdex) {
                    if (inner.length <= 0) return inner;
                    var el = $.parseHTML(inner);
                    var result = '';
                    $.each(el, function (index, item) {
                      if (item.classList !== undefined && item.classList.contains('category-name')) {
                        result = result + item.lastChild.firstChild.textContent;
                      } else if (item.innerText === undefined) {
                        result = result + item.textContent;
                      } else result = result + item.innerText;
                    });
                    return result;
                  }
                }
              }
            },
            {
              extend: 'copy',
              text: '<i class="ti ti-copy me-2"></i>Copy',
              className: 'dropdown-item',
              exportOptions: {
                columns: [1, 2, 3, 4, 5, 6, 7, 8],
                format: {
                  body: function (inner, coldex, rowdex) {
                    if (inner.length <= 0) return inner;
                    var el = $.parseHTML(inner);
                    var result = '';
                    $.each(el, function (index, item) {
                      if (item.classList !== undefined && item.classList.contains('category-name')) {
                        result = result + item.lastChild.firstChild.textContent;
                      } else if (item.innerText === undefined) {
                        result = result + item.textContent;
                      } else result = result + item.innerText;
                    });
                    return result;
                  }
                }
              }
            }
          ]
        },
        {
          text: '<i class="ti ti-plus me-0 me-sm-1 ti-xs"></i><span class="d-none d-sm-inline-block">Add Category</span>',
          className: 'add-new btn btn-primary ms-2 ms-sm-0 waves-effect waves-light',
          action: function () {
            window.location.href = categoryAdd;
          }
        }
      ],
      responsive: {
        details: {
          display: $.fn.dataTable.Responsive.display.modal({
            header: function (row) {
              var data = row.data();
              return 'Details of ' + data['name'];
            }
          }),
          type: 'column',
          renderer: function (api, rowIdx, columns) {
            var data = $.map(columns, function (col, i) {
              return col.title !== ''
                ? '<tr data-dt-row="' + col.rowIndex + '" data-dt-column="' + col.columnIndex + '">' +
                  '<td>' + col.title + ':' + '</td> ' +
                  '<td>' + col.data + '</td>' +
                  '</tr>'
                : '';
            }).join('');
            return data ? $('<table class="table"/><tbody />').append(data) : false;
          }
        }
      },
      initComplete: function () {
        this.api()
          .columns(4)
          .every(function () {
            var column = this;
            var select = $(
              '<select id="CategoryType" class="form-select text-capitalize"><option value="">Type</option></select>'
            )
              .appendTo('.category_type')
              .on('change', function () {
                var val = $.fn.dataTable.util.escapeRegex($(this).val());
                column.search(val ? '^' + val + '$' : '', true, false).draw();
              });

            // Populate with unique type names from API (dynamic or static)
            var types = ['Type1', 'Type2', 'Type3']; // Placeholder; replace with API fetch if dynamic
            types.forEach(function (type) {
              select.append('<option value="' + type + '">' + type + '</option>');
            });
          });
        this.api()
          .columns(5)
          .every(function () {
            var column = this;
            var select = $(
              '<select id="CategoryDepartment" class="form-select text-capitalize"><option value="">Department</option></select>'
            )
              .appendTo('.category_department')
              .on('change', function () {
                var val = $.fn.dataTable.util.escapeRegex($(this).val());
                column.search(val ? '^' + val + '$' : '', true, false).draw();
              });

            // Populate with unique department names
            var departments = ['Dept1', 'Dept2', 'Dept3']; // Placeholder; replace with API fetch
            departments.forEach(function (dept) {
              select.append('<option value="' + dept + '">' + dept + '</option>');
            });
          });
        this.api()
          .columns(8)
          .every(function () {
            var column = this;
            var select = $(
              '<select id="CategoryStatus" class="form-select text-capitalize"><option value="">Status</option></select>'
            )
              .appendTo('.category_status')
              .on('change', function () {
                var val = $.fn.dataTable.util.escapeRegex($(this).val());
                column.search(val ? '^' + val + '$' : '', true, false).draw();
              });

            Object.keys(statusObj).forEach(function (key) {
              select.append('<option value="' + statusObj[key].title + '">' + statusObj[key].title + '</option>');
            });
          });
      }
    });
    $('.dataTables_length').addClass('mx-n2');
    $('.dt-buttons').addClass('d-flex flex-wrap mb-6 mb-sm-0');
  }

  // Filter form control to default size
  setTimeout(() => {
    $('.dataTables_filter .form-control').removeClass('form-control-sm');
    $('.dataTables_length .form-select').removeClass('form-select-sm');
  }, 300);
});