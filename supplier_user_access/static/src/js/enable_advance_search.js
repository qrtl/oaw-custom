odoo.define('supplier_user_access.EnableAdvanceSearch', function (require) {
    "use strict";

    var SearchView = require('web.SearchView');

    var EnableAdvanceSearch = SearchView.extend({
        start: function () {
            this._super.apply(this, arguments);
            debugger;
            var self = this;
            this.getSession().user_has_group('stock.group_stock_user').then(function (has_group) {
                if (has_group) {
                    $('o_searchview_more fa').show();
                }
            });
        },
    });
    return EnableAdvanceSearch;
});
