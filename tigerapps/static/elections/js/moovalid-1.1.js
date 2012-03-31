/*
Script: moovalid.js
Lite Mootools form validation library
*/

var validate = new Class({
		Implements: [Options, Events],
		options: {
			useAjaxSubmit:      false,
			AjaxSubmitOptions:	{}
		},	
		initialize: function(form, fields, options) {
			this.setOptions(options);
			this.form = $(form);
			this.fields = fields;
			this.errorinform = false;
			this.min = 0;
			this.max = 0;

			this.styleAdd();
			
			$each(this.fields, function(type, el){
				if($(el) != null){
					$(el).addEvent('blur', function(){
						this.check($(el), type);
					}.bind(this))
				}
			}.bind(this));
			
			$(this.form).addEvent('submit', function(e){
				return this.onSubmit(e);
			}.bind(this))
		},
		onSubmit: function(e){
			this.errorinform = false;
			$each(this.fields, function(type, el){
					this.check($(el), type);
			}.bind(this));
			if(this.errorinform){
				return false;
			} else {
				//alert(this.form.toQueryString());
				if(this.options.useAjaxSubmit){
					e.stop();
					this.form.set('send', this.options.	AjaxSubmitOptions);
					this.form.send();
				} else {
					this.form.submit();
				}
			}

		},
		check: function(el, type){
			this.rmerrm(el,type);
			var typeArray = type.split(' ');
			typeArray.each(function(item, index){
				if(item.contains('[')){
					var intItem = item.replace('[', '').replace(']','').split('-');
					this.min = intItem[0];
					this.max = intItem[1];
					item = 'Length';
				};
				if(item.contains('{')){
					var intItem = item.replace('{', '').replace('}','').split('-');
					this.min = intItem[0];
					this.max = intItem[1];
					item = 'Range';
				};

				if(!this.errored(el)){
					switch(item){
						case "Required":
							var reqTest = el.value.test(/[^.*]/);
							if(!reqTest) this.errm(el,item); else this.rmerrm(el);
							break;
					}
						
					if(el.value.test(/[^.*]/)){
						switch(item){
							case "Alphabetic":
								var alphabeticTest = el.value.test(/^[a-z ._-]+$/i);
								if(!alphabeticTest) this.errm(el,item); else this.rmerrm(el);
							break;
							case "AlphaNumeric":
								var alphaNumericTest = el.value.test(/^[a-z ._-]+$/i);
								if(!alphaNumericTest) this.errm(el,item); else this.rmerrm(el);
							break;
							case "Numeric":
								var numericTest = el.value.search(/[^0-9\.\,\s\-\_]/);
								if(!numericTest) this.errm(el,item); else this.rmerrm(el);
							break;

							case "Email":
								var emailTest = el.value.test(/^[a-z0-9._%-]+@[a-z0-9.-]+\.[a-z]{2,4}$/i);
								if(!emailTest) this.errm(el,item); else this.rmerrm(el);
							break;
							case "URL":
								var urlTest = el.value.test(/^(http|https|ftp)\:\/\/[a-z0-9\-\.]+\.[a-z]{2,3}(:[a-z0-9]*)?\/?([a-z0-9\-\._\?\,\'\/\\\+&amp;%\$#\=~])*$/i);
								if(!urlTest) this.errm(el,item); else this.rmerrm(el);
							break;
							case "Length":
								if(el.value.length < this.min || el.value.length > this.max ) {
									this.errm(el, item); 
								} else {
									this.rmerrm(el);
								}
							break;
							case "Range":
								if(el.value.toInt() < this.min || el.value.toInt() > this.max ) {
									this.errm(el, item); 
								} else {
									this.rmerrm(el);
								}
							break;

						}
					}
				}
			}.bind(this))
		},
		errored: function(el){
			if(el.hasClass('errorElement')) {
				return true; 
			}else {
				return false;
			}
		},
		errm: function(el, type){
			el.addClass('errorElement');
			var errel = new Element('span', {'class':'errorText'});
			var msg = this.getMsg(type);
			errel.set('text', msg);
			var parent = el.getParent();
			errel.inject(parent);
			this.errorinform = true;
		},
		rmerrm: function(el){
			if(el.getNext()){
				el.getNext().dispose();
				el.removeClass('errorElement');
			}
		},
		getMsg: function(type){
			switch(type){
				case "Required":           return " This field is required.";
				case "Alphabetic":         return " Cannot contain non-alphabetic characters.";
				case "Numeric":            return " Cannot contain non-numeric characters.";
				case "Range":			   return " The value must be between "+ this.min +" and "+this.max;
				case "Length":			   return " The length of string must be between "+this.min+" and "+this.max;
				case "Email":              return " Enter valid email address.";
				case "URL":				   return " Enter valid URL address.";
				case "AlphaNumeric":	   return " Cannot contain non-alphanumeric characters.";
				default:                   return " Undefined Error Message";
			}
		},
		styleAdd: function(){
			var style = '  .errorElement{ border:1px #FF0000 solid;  } ' + 
						'  .errorText{ color:#FF0000;efefef } ' ;
            var el = new Element('style', { 'type': 'text/css' });
			el.set('text', style);
			el.inject(document.head);
		}

})
