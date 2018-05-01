# -*- coding: utf-8 -*-
##############################################################################
#
#   Check Payment
#   Authors: Dominador B. Ramos Jr. <mongramosjr@gmail.com>
#   Company: Basement720 Technology Inc.
#
#   Copyright 2018 Dominador B. Ramos Jr.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
##############################################################################
import datetime

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

class CheckPaymentTransactionAbstract(models.AbstractModel):
    _name = "check.payment.transaction.abstract"
    _description = "Contains the logic shared between models which allows to register check payments"
    
    partner_id = fields.Many2one('res.partner', string='Partner')

    amount = fields.Monetary(string='Amount', required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, default=lambda self: self.env.user.company_id.currency_id)
    posted_date = fields.Date(string='Payment Date', required=False, copy=False)
    journal_id = fields.Many2one('account.journal', string='Journal', required=True, domain=[('type', 'in', ('bank', 'cash'))])
    company_id = fields.Many2one('res.company', related='journal_id.company_id', string='Company', readonly=True)
    
    @api.one
    @api.constrains('amount')
    def _check_amount(self):
        if self.amount < 0:
            raise ValidationError(_('The payment amount cannot be negative.'))

class CheckPaymentTransaction(models.Model):
    
    _name = 'check.payment.transaction'
    # inherit = 'check.payment.transaction.abstract' # doesnt include abstract model
    _inherit = ['mail.thread', 'check.payment.transaction.abstract']
    _description = 'Check Payment Transaction'
    _order = 'check_payment_date desc, check_name desc'
    
    state = fields.Selection([ ('draft', 'Draft'), 
    
        ('received', 'Received'), ('deposited', 'Deposited'),
        
        ('issued', 'Issued'),
        
        ('returned', 'Returned'), ('posted', 'Posted'), ('cancelled', 'Cancelled')
    ],
        required=True,
        default='draft',
        copy=False,
        string="Status"
    )
    
    name = fields.Char(readonly=True, copy=False, default="Draft Check Payment");
    check_name = fields.Char('Name', readonly=True, required=True, copy=False, states={'draft': [('readonly', False)]},)
    check_number = fields.Integer('Number', readonly=True, required=True, states={'draft': [('readonly', False)]}, copy=False)
    check_issue_date = fields.Date('Issue Date', readonly=True, copy=False, states={'draft': [('readonly', False)]}, default=fields.Date.context_today)
    check_payment_date = fields.Date('Payment Date', readonly=True, required=True, help="Only if this check is post dated", states={'draft': [('readonly', False)]})
    
    bank_account_id = fields.Many2one('res.partner.bank', string="Bank Account", ondelete='restrict', copy=False)
    bank_acc_number = fields.Char(related='bank_account_id.acc_number')
    bank_id = fields.Many2one('res.bank', related='bank_account_id.bank_id')

    account_payment_id = fields.Many2one('account.payment', string='Payment Reference', ondelete='cascade', index=True)
        
    @api.model
    def default_get(self, fields):
        rec = super(CheckPaymentTransaction, self).default_get(fields)
        
#        invoice_defaults = self.resolve_2many_commands('invoice_ids', rec.get('invoice_ids'))
#        if invoice_defaults and len(invoice_defaults) == 1:
#            invoice = invoice_defaults[0]
#            rec['currency_id'] = invoice['currency_id'][0]
#            rec['partner_id'] = invoice['partner_id'][0]
#            rec['journal_id'] = invoice['partner_id'][0]
#            rec['amount'] = invoice['residual']
        return rec
    
    @api.multi
    def received_check(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_("Only a draft check can be received."))
            
            
            rec.write({'state': 'received'})
            
            
    @api.multi
    def received_check(self):
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_("Only a draft check can be received."))
            
            
            rec.write({'state': 'received'})
    
    @api.multi
    def post(self):
        for rec in self:
            if rec.state != 'deposited' or rec.state != 'issued':
                raise UserError(_("Only a deposited or issued check can be posted."))
            
            
            rec.write({'state': 'posted'})
    
