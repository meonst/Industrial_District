
function toggle(selected_block) {
    chatlog_block = document.getElementById("chatlog")
    talents_block = document.getElementById("talents")
    stats_block = document.getElementById("stats")
    timeline_block = document.getElementById("timeline")
    charts_block = document.getElementById("charts")

    if (selected_block === "chatlog") {
        chatlog_block.style.display = "block"    
        talents_block.style.display = "none"    
        stats_block.style.display = "none"    
        timeline_block.style.display = "none"    
        charts_block.style.display = "none"
    }
    else if (selected_block === "talents") {
        chatlog_block.style.display = "none"   
        talents_block.style.display = "block"    
        stats_block.style.display = "none"    
        timeline_block.style.display = "none"    
        charts_block.style.display = "none" 
    }
    else if (selected_block === "stats") {
        chatlog_block.style.display = "none"    
        talents_block.style.display = "none"    
        stats_block.style.display = "block"    
        timeline_block.style.display = "none"
        charts_block.style.display = "none"     
    }
    else if (selected_block === "timeline") {
        chatlog_block.style.display = "none"    
        talents_block.style.display = "none"    
        stats_block.style.display = "none"    
        timeline_block.style.display = "block"        
        charts_block.style.display = "none"        
    }
    else if (selected_block === "charts") {
        chatlog_block.style.display = "none"    
        talents_block.style.display = "none"    
        stats_block.style.display = "none"    
        timeline_block.style.display = "none"        
        charts_block.style.display = "block"        
    }

}