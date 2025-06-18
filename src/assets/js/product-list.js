/**
 * app-ecommerce-product-list
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
  var dt_product_table = $('.datatables-products'),
    productAdd = '/products/add/',
    statusObj = {
      publish: { title: 'Publish', class: 'bg-label-success' },
      draft: { title: 'Draft', class: 'bg-label-warning' }
    },
    categoryObj = {
      Household: { title: 'Household', icon: 'ti-home-2' },
      Office: { title: 'Office', icon: 'ti-briefcase' },
      Electronics: { title: 'Electronics', icon: 'ti-device-mobile' },
      Shoes: { title: 'Shoes', icon: 'ti-shoe' },
      Accessories: { title: 'Accessories', icon: 'ti-device-watch' },
      Game: { title: 'Game', icon: 'ti-device-gamepad-2' }
    },
    stockObj = {
      true: { title: 'In_Stock' },
      false: { title: 'Out_of_Stock' }
    },
    stockFilterValObj = {
      true: { title: 'In Stock' },
      false: { title: 'Out of Stock' }
    };

  // E-commerce Products datatable
  if (dt_product_table.length) {
    var dt_products = dt_product_table.DataTable({
      ajax: '/api/products/', // DRF API endpoint
      columns: [
        { data: 'id' },
        { data: 'id' },
        { data: 'name' },
        { data: 'categories' },
        { data: 'in_stock' },
        { data: 'sku' },
        { data: 'standard_price' },
        { data: 'stock_quantity' },
        { data: 'status' },
        { data: '' }
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
              $brand = full['brand'] ? full['brand'].name : 'No Brand',
              $image = full['featured_image'];
            var $output = $image
              ? '<img src="' + $image + '" alt="Product-' + $id + '" class="rounded-2">'
              : '<span class="avatar-initial rounded-2 bg-label-secondary">' + $name.charAt(0).toUpperCase() + '</span>';
            return (
              '<div class="d-flex justify-content-start align-items-center product-name">' +
              '<div class="avatar-wrapper">' +
              '<div class="avatar avatar me-4 rounded-2 bg-label-secondary">' +
              $output +
              '</div>' +
              '</div>' +
              '<div class="d-flex flex-column">' +
              '<h6 class="text-nowrap mb-0">' + $name + '</h6>' +
              '<small class="text-truncate d-none d-sm-block">' + $brand + '</small>' +
              '</div>' +
              '</div>'
            );
          }
        },
        {
          targets: 3,
          responsivePriority: 5,
          render: function (data, type, full, meta) {
            var $categories = full['categories'].length ? full['categories'][0].name : 'Uncategorized';
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
          targets: 4,
          orderable: false,
          responsivePriority: 3,
          render: function (data, type, full, meta) {
            var $stock = full['in_stock'];
            var stockSwitchObj = {
              Out_of_Stock:
                '<label class="switch switch-primary switch-sm">' +
                '<input type="checkbox" class="switch-input" id="switch">' +
                '<span class="switch-toggle-slider">' +
                '<span class="switch-off"></span>' +
                '</span>' +
                '</label>',
              In_Stock:
                '<label class="switch switch-primary switch-sm">' +
                '<input type="checkbox" class="switch-input" checked="">' +
                '<span class="switch-toggle-slider">' +
                '<span class="switch-on"></span>' +
                '</span>' +
                '</label>'
            };
            return (
              "<span class='text-truncate'>" +
              stockSwitchObj[stockObj[$stock].title] +
              '<span class="d-none">' + stockObj[$stock].title + '</span>' +
              '</span>'
            );
          }
        },
        {
          targets: 5,
          render: function (data, type, full, meta) {
            var $sku = full['sku'] || 'N/A';
            return '<span>' + $sku + '</span>';
          }
        },
        {
          targets: 6,
          render: function (data, type, full, meta) {
            var $price = full['standard_price'] ? '$' + parseFloat(full['standard_price']).toFixed(2) : 'N/A';
            return '<span>' + $price + '</span>';
          }
        },
        {
          targets: 7,
          responsivePriority: 4,
          render: function (data, type, full, meta) {
            var $qty = full['stock_quantity'] || 0;
            return '<span>' + $qty + '</span>';
          }
        },
        {
          targets: -2,
          render: function (data, type, full, meta) {
            var $status = full['status'];
            return (
              '<span class="badge ' + statusObj[$status].class + '" text-capitalized>' +
              statusObj[$status].title +
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
              '<a href="/products/update/' + full['id'] + '" class="btn btn-sm btn-icon btn-text-secondary rounded-pill waves-effect waves-light"><i class="ti ti-edit ti-md"></i></a>' +
              '<button class="btn btn-sm btn-icon btn-text-secondary rounded-pill waves-effect waves-light dropdown-toggle hide-arrow" data-bs-toggle="dropdown"><i class="ti ti-dots-vertical ti-md"></i></button>' +
              '<div class="dropdown-menu dropdown-menu-end m-0">' +
              '<a href="/products/view/' + full['id'] + '/" class="dropdown-item">View</a>' +
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
      lengthMenu: [7, 10, 20, 50, 70, 100],
      language: {
        sLengthMenu: '_MENU_',
        search: '',
        searchPlaceholder: 'Search Product',
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
              text: '<i class="tSystem: i ti-printer me-2"></i>Print',
              className: 'dropdown-item',
              exportOptions: {
                columns: [1, 2, 3, 4, 5, 6, 7],
                format: {
                  body: function (inner, coldex, rowdex) {
                    if (inner.length <= 0) return inner;
                    var el = $.parseHTML(inner);
                    var result = '';
                    $.each(el, function (index, item) {
                      if (item.classList !== undefined && item.classList.contains('product-name')) {
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
                columns: [1, 2, 3, 4, 5, 6, 7],
                format: {
                  body: function (inner, coldex, rowdex) {
                    if (inner.length <= 0) return inner;
                    var el = $.parseHTML(inner);
                    var result = '';
                    $.each(el, function (index, item) {
                      if (item.classList !== undefined && item.classList.contains('product-name')) {
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
                columns: [1, 2, 3, 4, 5, 6, 7],
                format: {
                  body: function (inner, coldex, rowdex) {
                    if (inner.length <= 0) return inner;
                    var el = $.parseHTML(inner);
                    var result = '';
                    $.each(el, function (index, item) {
                      if (item.classList !== undefined && item.classList.contains('product-name')) {
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
                columns: [1, 2, 3, 4, 5, 6, 7],
                format: {
                  body: function (inner, coldex, rowdex) {
                    if (inner.length <= 0) return inner;
                    var el = $.parseHTML(inner);
                    var result = '';
                    $.each(el, function (index, item) {
                      if (item.classList !== undefined && item.classList.contains('product-name')) {
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
                columns: [1, 2, 3, 4, 5, 6, 7],
                format: {
                  body: function (inner, coldex, rowdex) {
                    if (inner.length <= 0) return inner;
                    var el = $.parseHTML(inner);
                    var result = '';
                    $.each(el, function (index, item) {
                      if (item.classList !== undefined && item.classList.contains('product-name')) {
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
          text: '<i class="ti ti-plus me-0 me-sm-1 ti-xs"></i><span class="d-none d-sm-inline-block">Add Product</span>',
          className: 'add-new btn btn-primary ms-2 ms-sm-0 waves-effect waves-light',
          action: function () {
            window.location.href = productAdd;
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
          .columns(-2)
          .every(function () {
            var column = this;
            var select = $(
              '<select id="ProductStatus" class="form-select text-capitalize"><option value="">Status</option></select>'
            )
              .appendTo('.product_status')
              .on('change', function () {
                var val = $.fn.dataTable.util.escapeRegex($(this).val());
                column.search(val ? '^' + val + '$' : '', true, false).draw();
              });

            Object.keys(statusObj).forEach(function (key) {
              select.append('<option value="' + statusObj[key].title + '">' + statusObj[key].title + '</option>');
            });
          });
        this.api()
          .columns(3)
          .every(function () {
            var column = this;
            var select = $(
              '<select id="ProductCategory" class="form-select text-capitalize"><option value="">Category</option></select>'
            )
              .appendTo('.product_category')
              .on('change', function () {
                var val = $.fn.dataTable.util.escapeRegex($(this).val());
                column.search(val ? '^' + val + '$' : '', true, false).draw();
              });

            Object.keys(categoryObj).forEach(function (key) {
              select.append('<option value="' + categoryObj[key].title + '">' + categoryObj[key].title + '</option>');
            });
          });
        this.api()
          .columns(4)
          .every(function () {
            var column = this;
            var select = $(
              '<select id="ProductStock" class="form-select text-capitalize"><option value=""> Stock </option></select>'
            )
              .appendTo('.product_stock')
              .on('change', function () {
                var val = $.fn.dataTable.util.escapeRegex($(this).val());
                column.search(val ? '^' + val + '$' : '', true, false).draw();
              });

            Object.keys(stockObj).forEach(function (key) {
              select.append('<option value="' + stockObj[key].title + '">' + stockFilterValObj[key].title + '</option>');
            });
          });
      }
    });
    $('.dataTables_length').addClass('mx-n2');
    $('.dt-buttons').addClass('d-flex flex-wrap mb-6 mb-sm-0');
  }

  // Delete Record
  $('.datatables-products tbody').on('click', '.delete-record', function () {
    var productId = $(this).data('id');
    if (confirm('Are you sure you want to delete this product?')) {
      $.ajax({
        url: '/api/products/' + productId + '/',
        type: 'DELETE',
        success: function () {
          dt_products.row($(this).parents('tr')).remove().draw();
        },
        error: function (xhr) {
          alert('Failed to delete product: ' + xhr.responseJSON?.detail || 'Unknown error');
        }
      });
    }
  });

  // Filter form control to default size
  setTimeout(() => {
    $('.dataTables_filter .form-control').removeClass('form-control-sm');
    $('.dataTables_length .form-select').removeClass('form-select-sm');
  }, 300);
});