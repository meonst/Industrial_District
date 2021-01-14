function toggle(selected_block) {
    chatlog_block = document.getElementById("chatlog")
    talents_block = document.getElementById("talents")
    stats_block = document.getElementById("stats")
    statistics_block = document.getElementById("statistics")
    charts_block = document.getElementById("charts")
    newCharts_block = document.getElementById("newCharts")
    if (selected_block === "chatlog") {
        chatlog_block.style.display = "block"    
        talents_block.style.display = "none"    
        stats_block.style.display = "none"    
        statistics_block.style.display = "none"    
        charts_block.style.display = "none"
        newCharts_block.style.display = "none"      
    }
    else if (selected_block === "talents") {
        chatlog_block.style.display = "none"   
        talents_block.style.display = "block"    
        stats_block.style.display = "none"    
        statistics_block.style.display = "none"    
        charts_block.style.display = "none"
        newCharts_block.style.display = "none"      
    }
    else if (selected_block === "stats") {
        chatlog_block.style.display = "none"    
        talents_block.style.display = "none"    
        stats_block.style.display = "block"    
        statistics_block.style.display = "none"
        charts_block.style.display = "none"    
        newCharts_block.style.display = "none"      
    }
    else if (selected_block === "statistics") {
        chatlog_block.style.display = "none"    
        talents_block.style.display = "none"    
        stats_block.style.display = "none"    
        statistics_block.style.display = "block"        
        charts_block.style.display = "none"
        newCharts_block.style.display = "none"              
    }
    else if (selected_block === "charts") {
        chatlog_block.style.display = "none"    
        talents_block.style.display = "none"    
        stats_block.style.display = "none"    
        statistics_block.style.display = "none"        
        charts_block.style.display = "block"   
        newCharts_block.style.display = "none"           
    }
    else if (selected_block === "newCharts") {
        chatlog_block.style.display = "none"    
        talents_block.style.display = "none"    
        stats_block.style.display = "none"    
        statistics_block.style.display = "none"        
        charts_block.style.display = "none"  
        newCharts_block.style.display = "block"      
    }
}


