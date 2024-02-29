import { $ } from "/static/jquery/src/jquery.js";
export function say_hi(elt) {
    console.log("Say hi to", elt);
}
say_hi($("h1"));

export function make_table_sortable(table){
    const sortableCells = table.find('th.sortable');
    sortableCells.on('click', function(e){
        const index = $(e.target).index();
        const isAsc = $(e.target).hasClass('sort-asc');
        const isDesc = $(e.target).hasClass('sort-desc');
        sortableCells.removeClass('sort-asc').removeClass('sort-desc')
        if (!isAsc && !isDesc) {
            $(e.target).addClass('sort-asc');
        } else if (isAsc) {
            $(e.target).removeClass('sort-asc').addClass('sort-desc');
        } else {
            $(e.target).removeClass('sort-desc')
        }
        
        const rows = table.find('tbody tr').get();
        const rowsArray = $(rows).toArray();
        rowsArray.sort(function(a,b){
            if (isDesc) {
                const aValue = $(a).data("index");
                const bValue = $(b).data("index");
                
                return aValue - bValue;
            }
            const aValue = parseFloat($(a).children('td').eq(index).data('value'));
            const bValue = parseFloat($(b).children('td').eq(index).data('value'));
            const comparison = $(e.target).hasClass('sort-asc') ? aValue - bValue : bValue - aValue;
            return comparison;
        });
        $(rowsArray).appendTo(table.find('tbody'));
    });
}

export function make_form_async(form){
    form.on('submit', function(e){
        e.preventDefault();
        const formdata = new FormData(form.get(0));
        form.find('input').attr('disabled', 'disabled');
        form.find('button').attr('disabled', 'disabled');
        const url = window.location.href.slice(-3) + "submit/";
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        const settings = {
            "url": url,
            "data": formdata,
            "type": "POST",
            "processData": false,
            "contentType": false,
            "headers": {'X-CSRFToken': csrftoken},
            "mimeType": form.attr('enctype'),
            "success": function(){
                form.replaceWith("<p>Upload Succeeded</p>");
            },
            "error": function(e){
                console.log("Upload failed", e);
            }
        };
        $.ajax(settings);
    });
}
export function make_grade_hypothesized(table){
    $(table).before("<button>Hypothesize</button");
    const button = $(document).find('button');
    button.on('click', function(e){
        console.log()
        if(table.hasClass('hypothesized')){
            table.removeClass('hypothesized');
            button.text('Hypothesize');
            $(table.find("tfoot tr td:last-child").get()).text($(table.find("tfoot tr td:last-child").get()).data("value"));
        }
        else{
            table.addClass('hypothesized');
            button.text('Actual Grades');
        }
        
        let rows = table.find("tbody tr td:last-child").get();
        console.log(rows);
        const rowsArray = $(rows).toArray();
        for(let i = 0; i < rowsArray.length; i++){
            console.log(rows[i])
            if($(rows[i]).attr('data-value') == "Ungraded" || $(rows[i]).attr('data-value') == "Not Due"){
                if(table.hasClass('hypothesized')){
                    $(rows[i]).replaceWith("<td class='numbercolumn' data-weight='" + $(rows[i]).attr('data-weight') + "'data-value='" + $(rows[i]).attr('data-value') + "'><input type=number></td>");
                }
                else{
                    $(rows[i]).replaceWith("<td class='numbercolumn' data-weight='" + $(rows[i]).attr('data-weight') + "'data-value='" + $(rows[i]).attr('data-value') + "'>" + $(rows[i]).attr('data-value') + "</td>");
                }
            }
        }
        rows = table.find("tbody tr td:last-child").get();
        const inputs = table.find("input");
        inputs.on("change", function(e){
            let finalpercent = 0;
            let finalweight = 0;
            //console.log(e.target.value);
            for(let i = 0; i < rowsArray.length; i++){
                if($(rows[i]).attr('data-value') == "Ungraded" || $(rows[i]).attr('data-value') == "Not Due"){
                    if(!($(rows[i]).find('input').val() === "")){
                        finalpercent += +$(rows[i]).find('input').val() * parseFloat($(rows[i]).attr('data-weight'));
                        finalweight += parseFloat($(rows[i]).attr('data-weight'));
                    }
                    
                }
                else if($(rows[i]).attr('data-value') == "Missing"){
                    finalweight += parseFloat($(rows[i]).attr('data-weight'));
                }
                else{
                    finalpercent += parseFloat($(rows[i]).attr('data-value')) * parseFloat($(rows[i]).attr('data-weight'));
                    finalweight += parseFloat($(rows[i]).attr('data-weight'));
                }
                
            }
            console.log(finalpercent);
            console.log(finalweight);
            console.log(finalpercent / finalweight);
            $(table.find("tfoot tr td:last-child").get()).text((finalpercent / finalweight).toFixed(2) + "%");
        })
        
    })
}
