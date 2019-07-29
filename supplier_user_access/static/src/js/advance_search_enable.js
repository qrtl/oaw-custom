// License, author and contributors information in:
// __openerp__.py file at the root folder of this module.

openerp.model_security_adjust_oaw = function (instance) {
    instance.web.ListView.include({
        load_list: function () {
            var self = this;
            this._super.apply(self, arguments);
            new openerp.web.Model('res.users').call('has_group', ['stock.group_stock_user'])
                .then(function (advance_search_enable) {
                    self.options.advance_search_enable = advance_search_enable;
                    if (advance_search_enable) {
                        $('.oe_searchview_drawer .col-md-5').show();
                    }
                });
        }
    });
};
