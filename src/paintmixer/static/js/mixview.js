
function rgb2hex(rgb) {
	function hex(x) {
	    return ("0" + parseInt(x).toString(16)).slice(-2);
	}

    rgb = rgb.match(/^rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*(\d+))?\)$/);
    return "#" + hex(rgb[1]) + hex(rgb[2]) + hex(rgb[3]);
}


function rgb2cmyk(rgb) {
	rgb = rgb.match(/^rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*(\d+))?\)$/);

    k = 1.0 - Math.max(rgb[1],rgb[2],rgb[3])/255.0;
	f = 1.0 - k;
	if (! f) {
		c = 0; m = 0; y = 0;
	} else {
	    c = Math.round(100 * (1 - rgb[1]/255.0 - k) / f);
	    m = Math.round(100 * (1 - rgb[2]/255.0 - k) / f);
	    y = Math.round(100 * (1 - rgb[3]/255.0 - k) / f);		
	}
	return [parseInt(c),parseInt(m),parseInt(y),parseInt(k*100)];
}


function cmyk2hex(c, m, y, k) {
	function hex(x) {
	    return ("0" + parseInt(x).toString(16)).slice(-2);
	}
	
    k = Math.min(k,100)
    r = 255 * (1 - Math.min(c, 100)/100.0) * (1 - k/100.0)
    g = 255 * (1 - Math.min(m, 100)/100.0) * (1 - k/100.0)
    b = 255 * (1 - Math.min(y, 100)/100.0) * (1 - k/100.0)
    return "#" + hex(r) + hex(g) + hex(b);	
}


function hexToRGB(hex) {
    var r = parseInt(hex.slice(1, 3), 16),
        g = parseInt(hex.slice(3, 5), 16),
        b = parseInt(hex.slice(5, 7), 16);

    return 'rgb(' + r + ', ' + g + ', ' + b + ')';
}

function set_palettes() {
	if (localStorage) {
		palette_choice = $("select[name='palette_choice']");
		palette_name = $("input[name='palette_name']");
		current = palette_name.val();
		if (!current) current="";
		
		palette_names = JSON.parse(localStorage.getItem('palette_names'));
		if (current == "Default")
			$("div#reset").each(function(){
				save_palette();			
			});

		if (palette_names) {
			palette_names.forEach(function(v){
				if (v != "Default") {
					opt = $("<option>");
					opt.attr("value", v);
					if (current == v)
						opt.attr("selected", "selected");
					opt.text(v);
					palette_choice.append(opt);
				}
			});
		}
	}
}


function enableButtons(){
	colournames = $("span.name_text").map(function(i, t){return $(t).text()}).get();
	cname = $("input[name='colourname']").val();
	if (colournames.includes(cname) || cname.length == 0) {
		$("input[name='bn_add']").prop('disabled', true);
	} else {
		$("input[name='bn_add']").prop('disabled', false);		
	}
	if (colournames.includes(cname)) {
		$("input[name='bn_remove']").prop('disabled', false);
		$("input[name='bn_mix']").prop('disabled', true);
	} else {
		$("input[name='bn_remove']").prop('disabled', true);		
		$("input[name='bn_mix']").prop('disabled', false);
	}
	if (colournames.length == 1) {
		$("input[name='bn_remove']").prop('disabled', true);				
	}
	$("input[name='bn_save_palette']").prop('disabled', false);
	$("input[name='bn_forget_palette']").prop('disabled', false);
	palette_name = $("input[name='palette_name']").val();
	if (palette_name == "Default") {
		$("input[name='bn_save_palette']").prop('disabled', true);
		$("input[name='bn_forget_palette']").prop('disabled', true);
	}
}


function update_colour() {
	c = $("input[name='cyan']").val();
	m = $("input[name='magenta']").val();
	y = $("input[name='yellow']").val();
	k = $("input[name='black']").val();
	hex = cmyk2hex(c, m, y, k);
	$("input[name='colour']").val(hex);
	$("#hexcolour").text(hex);
}


function save_palette() {
	if (localStorage) {
		palette_names = JSON.parse(localStorage.getItem('palette_names'));
		if (!palette_names) palette_names=[];
		current = $("input[name='palette_name']").val();
		if (current.length) {
    		if (!palette_names.includes(current)) {
        		palette_names.push(current);            		
        		localStorage.setItem('palette_names', JSON.stringify(palette_names));
    		}
    		palettes = JSON.parse(localStorage.getItem('palettes'));
    		if (!palettes) palettes={};    		
    		palette = $("input[name='palette']").val();
    		palettes[current] = palette;
    		localStorage.setItem('palettes', JSON.stringify(palettes));
		}
	}
}

function forget_palette() {
	if (localStorage) {
		palette_names = JSON.parse(localStorage.getItem('palette_names'));
		current = $("input[name='palette_name']").val();
		if (Array.isArray(palette_names) && palette_names.includes(current)) {
			i = palette_names.findIndex(function(name){
				return name==current;
			});
			palette_names.splice(i, 1);
		}
		localStorage.setItem('palette_names', JSON.stringify(palette_names));
		$("input[name='palette_name']").val("Default");
	}
}

$(document).ready(function(){
    $('div.scale-element').on('click', function(e){
    	index = parseInt($(this).attr('index'));
    	$(this).siblings().each(function(){
			$(this).removeClass('current');
			$('input', this).val(String(index+1));
		});
		$(this).addClass('current');
    	$(this).siblings().last();				
	});
	
    $('div.cmyk').on('click', function(e){
    	index = $(this).attr('index');
    	rgb = $(this).css('background-color');
    	hex = rgb2hex(rgb);
	    $("#hexcolour").text(hex);
    	
    	$("input[name='current']").val(index);
    	$("input[name='colour']").val(hex);
    	$('div.cmyk').removeClass('current');
    	$(this).addClass('current');
    	colourname = $(this).siblings('.name_text').text();
        instructions = $(this).siblings('.mix_text').text();
        if (instructions.length) {
            $(".mixes").removeClass("hidden");
            $(".mixes > .content").text(instructions);
        } else {
            $(".mixes").addClass("hidden");
        }
    	$("input[name='colourname']").val(colourname);
    	cmyk = rgb2cmyk(rgb);
    	$("input[name='cyan']").val(cmyk[0]);
    	$("input[name='magenta']").val(cmyk[1]);
    	$("input[name='yellow']").val(cmyk[2]);
    	$("input[name='black']").val(cmyk[3]);    	
        enableButtons();    	
    });
    
	
    $("input[name='colour']").change(function(){
    	$("input[name='colourname']").val("");
    	hex = $("input[name='colour']").val();
	    $("#hexcolour").text(hex);

    	rgb = hexToRGB(hex);
    	cmyk = rgb2cmyk(rgb);
    	$("input[name='cyan']").val(cmyk[0]);
    	$("input[name='magenta']").val(cmyk[1]);
    	$("input[name='yellow']").val(cmyk[2]);
    	$("input[name='black']").val(cmyk[3]);    	
        enableButtons();    	
    });
	$("input.cmykcolour").change(function(){ 
    	$("input[name='colourname']").val("");
		update_colour();
        enableButtons();
	});
	
    $('#bn_clear_palette').on('click', function(){
    	$("input[name='palette_name']").val(current);
    	if (localStorage) {
    		palettes = JSON.parse(localStorage.getItem('palettes'));
    		palette = palettes[current]
    		if (palette)
    			$("input[name='palette']").val(palette);    		
    	}
    	$("form[name='palette_form']").submit();		
    });
    
    $("input[name='colourname']").change(function(){
    	enableButtons();
    });
    $("select[name='palette_choice']").change(function(){
    	current = $("select[name='palette_choice']").val();
    	$("input[name='palette_name']").val(current);
    	if (localStorage) {
    		palettes = JSON.parse(localStorage.getItem('palettes'));
    		palette = palettes[current]
    		if (palette)
    			$("input[name='palette']").val(palette);    		
    	}
    	$("form[name='palette_form']").submit();
    });
    $("input[name='palette_name']").change(function(){
    	enableButtons();
    });
    
    $("input[name='bn_save_palette']").click(function(){
    	save_palette()
    });
    $("input[name='bn_forget_palette']").click(function(){
    	forget_palette();
    });
    set_palettes();
    enableButtons();
});
