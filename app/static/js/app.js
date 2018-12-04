/**
 * Sets URL when back button is hit.
 */
$(window).bind("popstate", function () {
    window.location = window.location.href;
});

let dashboardPageControllers = {
  initDashboardPage: () => {
        barsDataTableControllers.initBarsDataTable();

  }
};

let barsDataTableModels = {
    tableObj: null
};

let barsDataTableControllers = {
    /**
     * Setup bars DataTable.
     */
    initBarsDataTable: () => {
        let barsDataTable = $("#barsDataTable");

        //noinspection JSUnresolvedFunction
        barsDataTableModels.tableObj = barsDataTable.DataTable({
            orderCellsTop: true,
            columns: [
                {title: "Bar Name"},
                {title: "Score"},
                {title: "Group Score"},
                {title: "Comments"}
            ],
            dom: "lfip",
            order: [[0, "asc"]]
        });
        initDataTable(barsDataTableModels.tableObj, barsDataTable);
        barsDataTable.find("tbody")
            .on("click", "button.edit", function (e) {
                e.preventDefault();
                e.stopPropagation();
                let barId = $(this).closest("tr").attr("id");
                // let tableObj = barsDataTableModels.tableObj;
                //noinspection JSUnresolvedFunction
                // let barRow = tableObj.row(`#${barId}`);
                //noinspection JSUnresolvedFunction
                // let barName = tableObj.cell(barRow, tableObj.column("Name:name")).data();
                //noinspection JSUnresolvedFunction
                // let barDescription = tableObj.cell(barRow, tableObj.column("Description:name")).data();
                // barsDataTableViews.renderEditModal(barName, barDescription);
                // barsDataTableControllers.initEditModal(barId);
            });

    }
};

/**
 * Stops events from bubbling past a certain event.
 * @param event
 */
function stopPropagation (event) {
    if (event.stopPropagation !== undefined) {
        event.stopPropagation();
    } else {
        event.cancelBubble = true;
    }
}

/**
 * Setup for all DataTables.
 * @param table
 * @param datatable
 */
function initDataTable (table, datatable) {
    // Setup - add a text input to each header cell
    datatable.find("thead th").each(function (i) {
        let title = datatable.find("thead th").eq($(this).index()).text();
        if (title !== "Actions" && title !== "Add" && title !== "Edit" && title !== "Delete" && title !== "Select") {
            $(this).html(`${title}<br><input type="text" onclick="stopPropagation(event);" data-index="${i}" />`);
        }
    });

    // Filter event handler
    $(table.table().container()).on("keyup", "thead input", function () {
        //noinspection JSUnresolvedFunction
        table.column($(this).data("index")).search(this.value).draw();
    });
}