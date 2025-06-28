/**
 * DataTables Row Grouping for Product Variations
 */
'use strict';

$(function () {
  var dt_row_grouping_table = $('.dt-row-grouping');

  console.log('executed product-list.js');

  // Row Grouping
  // --------------------------------------------------------------------
  var groupColumn = 1; // product_name column
  if (dt_row_grouping_table.length) {
    var groupingTable = dt_row_grouping_table.DataTable({
      ajax: '/api/products/',
      columns: [
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
        { data: null, defaultContent: '<input type="number" class="form-control qty-input" min="0.01" step="0.01" value="1.00">' }, // Quantity (Decimal)
        { data: 'is_active' } // Status
      ],
      columnDefs: [
        {
          targets: 0,
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
          targets: 2, // Image
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
          targets: 3, // Department
          render: function (data, type, full, meta) {
            return data && data.name ? data.name : 'N/A';
          }
        },
        {
          targets: 4, // Category
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
              "<span class='text-truncate d-flex align-items-center textCls-heading'>" +
              (categoryBadgeObj[$categories] || '') + $categories +
              '</span>'
            );
          }
        },
        {
          targets: 5, // Brand
          render: function (data, type, full, meta) {
            var supplierNames = data && data.length ? data.map(s => s.name).join('<br>') : '-';
            return '<span class="text-truncate text-xs">' + supplierNames + '</span>';
          }
        },
        {
          targets: 6, // Price
          render: function (data, type, full, meta) {
            return data ? '' + parseFloat(data).toFixed(2) : 'N/A';
          }
        },
        {
          targets: 7, // Barcode
          render: function (data, type, full, meta) {
            return data || 'N/A';
          }
        },
        {
          targets: 8, // SKU
          render: function (data, type, full, meta) {
            return data || 'N/A';
          }
        },
        {
          targets: 9, // Stock
          render: function (data, type, full, meta) {
            return data !== null ? data : 0;
          }
        },
        {
          targets: 10, // Quantity
          orderable: false,
          searchable: false
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
                .before('<tr class="group"><td colspan="11">' + group + '</td></tr>'); // Colspan remains 11
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

    // Handle Add Selected Products button click
    $('#addSelectedProducts').on('click', function () {
      var selectedData = [];
      var errors = [];

      // Get all selected rows
      groupingTable.$('input.dt-checkboxes:checked').each(function () {
        var row = $(this).closest('tr');
        var rowData = groupingTable.row(row).data();
        var quantity = row.find('.qty-input').val();
        quantity = parseFloat(quantity);

        // Validate quantity
        if (isNaN(quantity) || quantity <= 0) {
          errors.push('Invalid quantity for variation: ' + rowData.title);
          return;
        }

        // // Validate stock (optional)
        // if (quantity > (rowData.stock_quantity || 0)) {
        //   errors.push('Quantity exceeds stock for variation: ' + rowData.title);
        //   return;
        // }

        selectedData.push({
          variation_id: rowData.id,  // Changed from product_id
          quantity: quantity
        });
      });

      // Handle errors
      if (errors.length > 0) {
        alert('Please fix the following errors:\n' + errors.join('\n'));
        return;
      }

      // Check if any variations were selected
      if (selectedData.length === 0) {
        alert('Please select at least one variation.');
        return;
      }

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

      var csrftoken = getCookie('csrftoken');
      // Get purchase_order_id from hidden input
      var purchaseOrderId = $('#purchaseOrderId').val();

      // Validate purchase_order_id
      if (!purchaseOrderId) {
        alert('Purchase order ID is missing.');
        return;
      }

      // Send AJAX request to create purchase order items
      $.ajax({
        url: '/api/po-item/bulk-create/',
        type: 'POST',
        headers: {
          'X-CSRFToken': csrftoken
        },
        data: JSON.stringify({
          items: selectedData,
        //   purchase_order_id: $('#purchaseOrderId').val() || 1 // Replace with dynamic purchase order ID
          purchase_order_id: purchaseOrderId
        }),
        contentType: 'application/json',
        success: function (response) {
          $('#productSelectionModal').modal('hide'); // Close the modal
          setTimeout(function () {
            window.location.reload(); // Refresh the page after 1 second
          }, 1000);
          alert('Purchase order items created successfully!');
        },
        error: function (xhr) {
          var errorMsg = 'Failed to create purchase order items.';
          if (xhr.responseJSON && xhr.responseJSON.error) {
            errorMsg += '\n' + xhr.responseJSON.error;
          }
          alert(errorMsg);
        }
      });
    });
  }
});