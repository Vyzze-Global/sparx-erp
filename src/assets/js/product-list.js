/**
 * DataTables Row Grouping for Product Variations
 */
'use strict';

$(function () {
  var dt_row_grouping_table = $('.dt-row-grouping');

  console.log('executed product-list.js');

  // Row Grouping
  // --------------------------------------------------------------------
  var groupColumn = 2; // product_name column
  if (dt_row_grouping_table.length) {
    var groupingTable = dt_row_grouping_table.DataTable({
      ajax: '/api/products/',
      columns: [
        { data: '' }, // Control
        { data: 'id' }, // ID (checkbox)
        { data: 'product_name' }, // Product Name (grouping)
        { data: 'variation_image' }, // Image
        { data: 'department' }, // Department
        { data: 'categories' }, // Category
        { data: 'suppliers' }, // Suppliers
        { data: 'standard_price' }, // Price
        { data: 'barcode' }, // Barcode
        { data: 'sku' }, // SKU
        { data: 'stock_quantity' }, // Stock
        { data: 'is_active' }, // Status
        { data: '' } // Actions
      ],
      columnDefs: [
        {
          className: 'control',
          orderable: false,
          targets: 0,
          searchable: false,
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
        { visible: false, targets: groupColumn }, // Hide product_name column
        {
          targets: 3, // Image (Variation)
          responsivePriority: 1,
          render: function (data, type, full, meta) {
            var $title = full['title'],
              $id = full['id'],
              $brand = full['brand'] && full['brand'].name ? full['brand'].name : 'No Brand',
              $image = full['variation_image'] || full['product_image'];
            var $output = $image
              ? '<img src="' + $image + '" alt="Product-' + $id + '" class="rounded-2">'
              : '<span class="avatar-initial rounded-2 bg-label-secondary">' + $title.charAt(0).toUpperCase() + '</span>';
            return (
              '<div class="d-flex justify-content-start align-items-center product-name">' +
              '<div class="avatar-wrapper">' +
              '<div class="avatar avatar me-4 rounded-2 bg-label-secondary">' +
              $output +
              '</div>' +
              '</div>' +
              '<div class="d-flex flex-column">' +
              '<h6 class="text-nowrap mb-0">' + $title + '</h6>' +
              '<small class="text-truncate d-none d-sm-block">' + $brand + '</small>' +
              '</div>' +
              '</div>'
            );
          }
        },
        {
          targets: 4, // Department
          render: function (data, type, full, meta) {
            return data && data.name ? data.name : 'N/A';
          }
        },
        {
          targets: 5, // Category
          responsivePriority: 5,
          render: function (data, type, full, meta) {
            var $categories = data.length ? data[0].name : 'Uncategorized';
            var categoryBadgeObj = {
              Household: '<span class="avatar-sm rounded-circle d-flex justify-content-center align-items-center bg-label-warning me-4 p-3"><i class="ti ti-home-2 ti-sm"></i></span>',
              Office: '<span class="avatar-sm rounded-circle d-flex justify-content-center align-items-center bg-label-info me-4 p-3"><i class="ti ti-briefcase ti-sm"></i></span>',
              Electronics: '<span class="avatar-sm rounded-circle d-flex justify-content-center align-items-center bg-label-danger me-4 p-3"><i class="ti ti-device-mobile ti-sm"></i></span>',
              Shoes: '<span class="avatar-sm rounded-circle d-flex justify-content-center align-items-center bg-label-success me-4"><i class="ti ti-shoe ti-sm"></i></span>',
              Accessories: '<span class="avatar-sm rounded-circle d-flex justify-content-center align-items-center bg-label-secondary me-4"><i class="ti ti-device-watch ti-sm"></i></span>',
              Game: '<span class="avatar-sm rounded-circle d-flex justify-content-center align-items-center bg-label-primary me-4"><i class="ti ti-device-gamepad-2 ti-sm"></i></span>'
            };
            return (
              "<span class='text-truncate d-flex align-items-center text-heading'>" +
              (categoryBadgeObj[$categories] || '') + $categories +
              '</span>'
            );
          }
        },
        {
          targets: 6, // Suppliers (replaced Brand)
          render: function (data, type, full, meta) {
            var supplierNames = data && data.length ? data.map(s => s.name).join('<br>') : '-';
            return '<span class="text-truncate text-xs">' + supplierNames + '</span>';
          }
        },
        {
          targets: 7, // Price
          render: function (data, type, full, meta) {
            return data ? '' + parseFloat(data).toFixed(2) : 'N/A';
          }
        },
        {
          targets: 8, // Barcode
          render: function (data, type, full, meta) {
            return data || 'N/A';
          }
        },
        {
          targets: 9, // SKU
          render: function (data, type, full, meta) {
            return data || 'N/A';
          }
        },
        {
          targets: 10, // Stock
          render: function (data, type, full, meta) {
            return data !== null ? data : 0;
          }
        },
        {
          targets: 11, // Status
          render: function (data, type, full, meta) {
            var status = {
              true: { title: 'Active', class: 'bg-label-success' },
              false: { title: 'Inactive', class: 'bg-label-secondary' }
            };
            return (
              '<span class="badge ' + status[data].class + '">' + status[data].title + '</span>'
            );
          }
        },
        {
          targets: -1, // Actions
          title: 'Actions',
          orderable: false,
          searchable: false,
          render: function (data, type, full, meta) {
            return (
              '<div class="d-inline-block">' +
              '<a href="/products/update/' + full['product_id'] + '#variation-' + full['id'] + '" class="btn btn-sm btn-text-secondary rounded-pill btn-icon"><i class="ti ti-pencil ti-md"></i></a>' +
              '<a href="javascript:;" class="btn btn-sm btn-text-secondary rounded-pill btn-icon dropdown-toggle hide-arrow" data-bs-toggle="dropdown"><i class="ti ti-dots-vertical ti-md"></i></a>' +
              '<div class="dropdown-menu dropdown-menu-end m-0">' +
              '<a href="/products/update/' + full['product_id'] + '" class="dropdown-item">Edit Product</a>' +
              '</div>' +
              '</div>'
            );
          }
        }
      ],
      order: [[groupColumn, 'asc']],
      dom: '<"row"<"col-sm-12 col-md-6"l><"col-sm-12 col-md-6 d-flex justify-content-center justify-content-md-end mt-n6 mt-md-0"f>>t<"row"<"col-sm-12 col-md-6"i><"col-sm-12 col-md-6"p>>',
      displayLength: 7,
      lengthMenu: [7, 10, 25, 50, 75, 100],
      language: {
        paginate: {
          next: '<i class="ti ti-chevron-right ti-sm"></i>',
          previous: '<i class="ti ti-chevron-left ti-sm"></i>'
        }
      },
      drawCallback: function (settings) {
        var api = this.api();
        var rows = api.rows({ page: 'current' }).nodes();
        var last = null;

        api
          .column(groupColumn, { page: 'current' })
          .data()
          .each(function (group, i) {
            if (last !== group) {
              $(rows)
                .eq(i)
                .before('<tr class="group"><td colspan="12">' + group + '</td></tr>'); // Colspan remains 12
              last = group;
            }
          });
      },
      responsive: {
        details: {
          display: $.fn.dataTable.Responsive.display.modal({
            header: function (row) {
              var data = row.data();
              return 'Details of ' + data['title'];
            }
          }),
          type: 'column',
          renderer: function (api, rowIdx, columns) {
            var data = $.map(columns, function (col, i) {
              return col.title !== ''
                ? '<tr data-dt-row="' +
                    col.rowIndex +
                    '" data-dt-column="' +
                    col.columnIndex +
                    '">' +
                    '<td>' +
                    col.title +
                    ':' +
                    '</td> ' +
                    '<td>' +
                    col.data +
                    '</td>' +
                    '</tr>'
                : '';
            }).join('');

            return data ? $('<table class="table"/><tbody />').append(data) : false;
          }
        }
      }
    });

    // Order by the grouping
    $('.dt-row-grouping tbody').on('click', 'tr.group', function () {
      var currentOrder = groupingTable.order()[0];
      if (currentOrder[0] === groupColumn && currentOrder[1] === 'asc') {
        groupingTable.order([groupColumn, 'desc']).draw();
      } else {
        groupingTable.order([groupColumn, 'asc']).draw();
      }
    });

    // Get CSRF token
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
  }
});