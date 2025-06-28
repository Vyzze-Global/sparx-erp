/**
 * App Purchase Order List
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
  var dt_po_table = $('.datatables-po-list'),
    poAdd = '/po/add/',
    statusObj = {
      draft: { title: 'Draft', class: 'bg-label-secondary' },
      submitted: { title: 'Submitted', class: 'bg-label-primary' },
      approved: { title: 'Approved', class: 'bg-label-success' },
      partially_received: { title: 'Partially Received', class: 'bg-label-success' },
      fully_received: { title: 'Fully Received', class: 'bg-label-success' },
      cancelled: { title: 'Cancelled', class: 'bg-label-danger' }
    },
    // Map API status values to statusObj keys
    statusMap = {
      'Draft': 'draft',
      'Submitted': 'submitted',
      'Approved': 'approved',
      'Partially Received': 'partially_received',
      'Fully Received': 'fully_received',
      'Cancelled': 'cancelled'
    };

  // Custom search function for date range
  $.fn.dataTable.ext.search.push(function (settings, data, dataIndex) {
    var dateRangeInput = $('#PODateRange').val();
    if (!dateRangeInput) return true; // No filter applied

    var orderDate = data[5]; // Order Date column (index 5)
    if (!orderDate || orderDate === 'N/A') return false;

    var dates = dateRangeInput.split(' to ');
    if (dates.length !== 2) return true; // Invalid range

    var startDate = new Date(dates[0]);
    var endDate = new Date(dates[1]);
    var currentDate = new Date(orderDate);

    // Ensure valid dates
    if (isNaN(startDate) || isNaN(endDate) || isNaN(currentDate)) return true;

    return currentDate >= startDate && currentDate <= endDate;
  });

  // Purchase Orders datatable
  if (dt_po_table.length) {
    var dt_purchase_orders = dt_po_table.DataTable({
      ajax: '/api/pos/', // DRF API endpoint
      columns: [
        { data: '' }, // Control
        { data: 'id' }, // ID
        { data: 'po_number' }, // PO Number
        { data: 'supplier.name' }, // Supplier name
        { data: 'warehouse.name' }, // Warehouse name
        { data: 'order_date' }, // Order Date
        { data: 'status' }, // Status
        { data: 'expected_delivery_date' }, // Expected Delivery Date
        { data: 'total' }, // Total
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
            var $po_number = full['po_number'],
              $id = full['id'];
            return (
              '<div class="d-flex justify-content-start align-items-center po-number">' +
              '<div class="d-flex flex-column">' +
              '<h6 class="text-nowrap mb-0">PO#' + $po_number + '</h6>' +
              '</div>' +
              '</div>'
            );
          }
        },
        {
          targets: 3,
          render: function (data, type, full, meta) {
            return full['supplier'] && full['supplier']['name'] ? full['supplier']['name'] : 'N/A';
          }
        },
        {
          targets: 4,
          render: function (data, type, full, meta) {
            return full['warehouse'] && full['warehouse']['name'] ? full['warehouse']['name'] : 'N/A';
          }
        },
        {
          targets: 5,
          render: function (data, type, full, meta) {
            return full['order_date'] || 'N/A';
          }
        },
        {
          targets: 6,
          render: function (data, type, full, meta) {
            var $status = full['status'];
            var $statusKey = statusMap[$status] || $status;
            if (!statusObj[$statusKey]) {
              console.warn('Invalid status:', $status);
              return '<span class="badge bg-label-warning">Unknown</span>';
            }
            return (
              '<span class="badge ' + statusObj[$statusKey].class + '" text-capitalized>' +
              statusObj[$statusKey].title +
              '</span>'
            );
          }
        },
        {
          targets: 7,
          render: function (data, type, full, meta) {
            return full['expected_delivery_date'] || 'N/A';
          }
        },
        {
          targets: 8,
          render: function (data, type, full, meta) {
            return full['total'].toFixed(2);
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
              '<a href="/po/update/' + full['id'] + '" class="btn btn-sm btn-icon btn-text-secondary rounded-pill waves-effect waves-light"><i class="ti ti-edit ti-md"></i></a>' +
              '<button class="btn btn-sm btn-icon btn-text-secondary rounded-pill waves-effect waves-light dropdown-toggle hide-arrow" data-bs-toggle="dropdown"><i class="ti ti-dots-vertical ti-md"></i></button>' +
              '<div class="dropdown-menu dropdown-menu-end m-0">' +
              '<a href="/po/view/' + full['id'] + '/" class="dropdown-item">View</a>' +
              '<a href="javascript:0;" class="dropdown-item delete-record" data-id="' + full['id'] + '">Delete</a>' +
              '</div>' +
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
      lengthMenu: [10, 20, 50, 100],
      language: {
        sLengthMenu: '_MENU_',
        search: '',
        searchPlaceholder: 'Search Purchase Order',
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
                      if (item.classList && item.classList.contains('po-number')) {
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
                  .css('background-color', '#fff');
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
                      if (item.classList && item.classList.contains('po-number')) {
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
              text: '<i class="ti ti-file-excel me-2"></i>Excel',
              className: 'dropdown-item',
              exportOptions: {
                columns: [1, 2, 3, 4, 5, 6, 7, 8],
                format: {
                  body: function (inner, coldex, rowdex) {
                    if (inner.length <= 0) return inner;
                    var el = $.parseHTML(inner);
                    var result = '';
                    $.each(el, function (index, item) {
                      if (item.classList && item.classList.contains('po-number')) {
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
                      if (item.classList && item.classList.contains('po-number')) {
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
                      if (item.classList && item.classList.contains('po-number')) {
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
          text: '<i class="ti ti-plus me-0 me-sm-1 ti-xs"></i><span class="d-none d-sm-inline-block">Add Purchase Order</span>',
          className: 'add-new btn btn-primary ms-2 ms-sm-0 waves-effect waves-light',
          action: function () {
            window.location.href = poAdd;
          }
        }
      ],
      responsive: {
        details: {
          display: $.fn.dataTable.Responsive.display.modal({
            header: function (row) {
              var data = row.data();
              return 'Details of PO#' + data['po_number'];
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
        // Supplier filter
        this.api()
          .columns(3)
          .every(function () {
            var column = this;
            var select = $(
              '<select id="POSupplier" class="form-select text-capitalize"><option value="">All Suppliers</option></select>'
            )
            .appendTo('.po_supplier')
            .on('change', function () {
              var val = $.fn.dataTable.util.escapeRegex($(this).val());
              column.search(val ? '^' + val + '$' : '', true, false).draw();
            });

            // Fetch suppliers from API
            $.ajax({
              url: '/api/suppliers/',
              method: 'GET',
              dataType: 'json',
              success: function (response) {
                if (response && response.data && Array.isArray(response.data)) {
                  response.data.forEach(function (supplier) {
                    select.append('<option value="' + supplier.name + '">' + supplier.name + '</option>');
                  });
                } else {
                  console.error('Invalid supplier API response structure:', response);
                }
              },
              error: function (xhr) {
                console.error('Failed to fetch suppliers:', xhr);
              }
            });
          });

        // Warehouse filter
        this.api()
          .columns(4)
          .every(function () {
            var column = this;
            var select = $(
              '<select id="POWarehouse" class="form-select text-capitalize"><option value="">All Warehouses</option></select>'
            )
            .appendTo('.po_warehouse')
            .on('change', function () {
              var val = $.fn.dataTable.util.escapeRegex($(this).val());
              column.search(val ? '^' + val + '$' : '', true, false).draw();
            });

            // Fetch warehouses from API
            $.ajax({
              url: '/api/warehouses/',
              method: 'GET',
              dataType: 'json',
              success: function (response) {
                if (response && response.data && Array.isArray(response.data)) {
                  response.data.forEach(function (warehouse) {
                    select.append('<option value="' + warehouse.name + '">' + warehouse.name + '</option>');
                  });
                } else {
                  console.error('Invalid warehouse API response structure:', response);
                }
              },
              error: function (xhr) {
                console.error('Failed to fetch warehouses:', xhr);
              }
            });
          });

        // Date Range filter
        this.api()
          .columns(5)
          .every(function () {
            var column = this;
            var dateRange = $(
              '<input type="text" id="PODateRange" class="form-control flatpickr-range" placeholder="Select Date Range" />'
            )
            .appendTo('.po_date_range')
            .flatpickr({
              mode: 'range',
              dateFormat: 'Y-m-d',
              onChange: function (selectedDates, dateStr, instance) {
                // Trigger DataTable redraw to apply custom search
                column.draw();
              }
            });
          });
      }
    });
    $('.dataTables_length').addClass('mx-n2');
    $('.dt-buttons').addClass('d-flex flex-wrap mb-6 mb-sm-0');
  }

  // Delete Record
  $('.datatables-po-list tbody').on('click', '.delete-record', function () {
    var poId = $(this).data('id');
    if (confirm('Are you sure you want to delete this purchase order?')) {
      $.ajax({
        url: '/api/pos/' + poId + '/',
        type: 'DELETE',
        headers: { 'X-CSRFToken': getCookie('csrftoken') },
        success: function () {
          dt_purchase_orders.row($(this).parents('tr')).remove().draw();
        },
        error: function (xhr) {
          alert('Failed to delete purchase order: ' + xhr.responseJSON?.detail || 'Unknown error');
        }
      });
    }
  });

  // Get CSRF token for DELETE requests
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  // Filter form control to default size
  setTimeout(() => {
    $('.dataTables_filter .form-control').removeClass('form-control-sm');
    $('.dataTables_length .form-select').removeClass('form-select-sm');
  }, 300);
});