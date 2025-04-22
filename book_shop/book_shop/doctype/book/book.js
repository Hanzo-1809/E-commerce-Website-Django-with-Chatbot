frappe.ui.form.on('Book', {
    refresh: function (frm) {
        // Thêm nút để thay đổi trạng thái
        if (frm.doc.status !== "Published" && !frm.is_new()) {
            frm.add_custom_button(__('Publish'), function () {
                update_book_status(frm, "Published");
            });
        }

        if (frm.doc.status !== "Archived" && !frm.is_new()) {
            frm.add_custom_button(__('Archive'), function () {
                update_book_status(frm, "Archived");
            });
        }

        if (frm.doc.status !== "Draft" && !frm.is_new()) {
            frm.add_custom_button(__('Set as Draft'), function () {
                update_book_status(frm, "Draft");
            });
        }

        // Thêm nút để xem tất cả sách trong cùng danh mục
        if (frm.doc.category_id && !frm.is_new()) {
            frm.add_custom_button(__('View Books in Same Category'), function () {
                frappe.set_route('List', 'Book', { 'category_id': frm.doc.category_id });
            });
        }

        // Thêm chức năng xem trước hình ảnh thumbnail
        if (frm.doc.thumbnail) {
            frm.sidebar.add_image_view({
                label: 'Book Thumbnail',
                fieldname: 'thumbnail',
                title: 'Book Thumbnail Preview'
            });
        }
    },

    before_save: function (frm) {
        // Nếu không có giá thì đặt giá là 0
        if (!frm.doc.price) {
            frm.set_value('price', 0);
        }
    },

    validate: function (frm) {
        // Kiểm tra ID hợp lệ
        if (frm.doc.id) {
            let id_pattern = /^[a-zA-Z0-9-_]+$/;
            if (!id_pattern.test(frm.doc.id)) {
                frappe.throw(__('ID chỉ được chứa chữ cái, số, dấu gạch ngang và gạch dưới'));
                validated = false;
            }
        }
    },

    // Xử lý khi trường thumbnail thay đổi
    thumbnail: function (frm) {
        if (frm.doc.thumbnail) {
            // Hiển thị thông báo khi tải ảnh thành công
            frappe.show_alert({
                message: __('Thumbnail uploaded successfully'),
                indicator: 'green'
            }, 3);

            // Làm mới sidebar để hiển thị hình ảnh
            frm.sidebar.refresh();
        }
    }
});

function update_book_status(frm, status) {
    frappe.call({
        method: "book_shop.book_module.doctype.book.book.update_book_status",
        args: {
            name: frm.doc.name,
            status: status
        },
        callback: function (r) {
            if (!r.exc) {
                frm.reload_doc();
                frappe.show_alert({
                    message: __('Book status updated to {0}', [status]),
                    indicator: 'green'
                });
            }
        }
    });
}