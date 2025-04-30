"""
استایل سفارشی برای رنگ‌بندی کد در پروژه H2
این استایل رنگ‌بندی زیر را اعمال می‌کند:
- استرینگ‌ها: سبز
- متغیرها: چند رنگ
- کلاس‌ها و فراخوانی‌هایشان: آلبالویی (رنگ شرابی)
"""

from pygments.style import Style
from pygments.token import (
    Token, Comment, Keyword, Name, String, Number, 
    Operator, Generic, Whitespace, Punctuation, Error
)


class CustomH2Style(Style):
    """
    استایل سفارشی برای پروژه H2 با رنگ‌بندی مشخص شده
    """

    name = 'custom_h2'

    # رنگ‌های پس‌زمینه و هایلایت
    background_color = '#1e1e1e'  # پس‌زمینه تیره
    highlight_color = '#2d2d2d'   # رنگ هایلایت

    # تعریف استایل‌ها
    styles = {
        # استایل پیش‌فرض
        Token:                  '#f8f8f2',
        
        # کامنت‌ها
        Comment:                'italic #6a9955',
        Comment.Preproc:        'noitalic #ff8080',
        Comment.Special:        'noitalic bold #ff8080',
        
        # کلیدواژه‌ها
        Keyword:                '#569cd6',
        Keyword.Declaration:    '#569cd6',
        Keyword.Namespace:      '#569cd6',
        Keyword.Pseudo:         '#569cd6',
        Keyword.Type:           '#4ec9b0',
        Keyword.Constant:       '#569cd6',
        
        # عملگرها
        Operator:               '#d4d4d4',
        Operator.Word:          '#569cd6',
        
        # نام‌ها
        Name:                   '#d4d4d4',
        Name.Builtin:           '#4ec9b0',
        Name.Builtin.Pseudo:    '#569cd6',
        Name.Class:             '#c586c0',  # کلاس‌ها به رنگ آلبالویی
        Name.Constant:          '#4fc1ff',
        Name.Decorator:         '#dcdcaa',
        Name.Entity:            '#4ec9b0',
        Name.Exception:         '#c586c0',
        Name.Function:          '#c586c0',  # توابع به رنگ آلبالویی
        Name.Function.Magic:    '#c586c0',
        Name.Label:             '#d4d4d4',
        Name.Namespace:         '#4ec9b0',
        Name.Tag:               '#569cd6',
        Name.Variable:          '#9cdcfe',  # متغیرها به رنگ آبی روشن
        Name.Variable.Class:    '#9cdcfe',
        Name.Variable.Global:   '#4fc1ff',
        Name.Variable.Instance: '#9cdcfe',
        Name.Variable.Magic:    '#569cd6',
        
        # رشته‌ها
        String:                 '#6a9955',  # استرینگ‌ها به رنگ سبز
        String.Affix:           '#6a9955',
        String.Backtick:        '#6a9955',
        String.Char:            '#6a9955',
        String.Delimiter:       '#6a9955',
        String.Doc:             '#6a9955',
        String.Double:          '#6a9955',
        String.Escape:          '#d7ba7d',
        String.Heredoc:         '#6a9955',
        String.Interpol:        '#6a9955',
        String.Other:           '#6a9955',
        String.Regex:           '#d16969',
        String.Single:          '#6a9955',
        String.Symbol:          '#6a9955',
        
        # اعداد
        Number:                 '#b5cea8',
        Number.Bin:             '#b5cea8',
        Number.Float:           '#b5cea8',
        Number.Hex:             '#b5cea8',
        Number.Integer:         '#b5cea8',
        Number.Integer.Long:    '#b5cea8',
        Number.Oct:             '#b5cea8',
        
        # عمومی
        Generic:                '#d4d4d4',
        Generic.Deleted:        '#f92672',
        Generic.Emph:           'italic',
        Generic.Error:          '#f92672',
        Generic.Heading:        'bold #569cd6',
        Generic.Inserted:       '#a6e22e',
        Generic.Output:         '#d4d4d4',
        Generic.Prompt:         'bold #569cd6',
        Generic.Strong:         'bold',
        Generic.Subheading:     'bold #569cd6',
        Generic.Traceback:      '#f92672',
        
        # سایر
        Punctuation:            '#d4d4d4',
        Whitespace:             '#bbbbbb',
        Error:                  '#f92672',
    }
