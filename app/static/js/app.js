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

let reviewPageControllers = {
    initReviewPage: () => {
        barsDataTableControllers.initBarsDataTable();

    }
};

function initMap() {
    let map = new google.maps.Map(document.getElementById('map'), {
        zoom: 18,
        center: {lat: 32.816, lng: -80.036}
    });
    let infowindow = new google.maps.InfoWindow({});
    let geocoder = new google.maps.Geocoder();
    $.get("/map_data", (data) => {
        data.forEach(function (item) {
            geocoder.geocode({'address': item.location}, function (results, status) {
                if (status === 'OK') {
                    if (item.current === true) {
                        let marker = new google.maps.Marker({
                            position: results[0].geometry.location,
                            map: map,
                            title: item.bar_name,
                            icon: "http://maps.google.com/mapfiles/ms/icons/green-dot.png"

                        });
                        map.setCenter(results[0].geometry.location);
                        marker.addListener('click', function () {
                            infowindow.setContent(marker.title);
                            infowindow.open(map, marker);
                        });
                    } else {
                        let marker = new google.maps.Marker({
                            position: results[0].geometry.location,
                            map: map,
                            title: item.bar_name,
                        });
                        marker.addListener('click', function () {
                            infowindow.setContent(marker.title);
                            infowindow.open(map, marker);
                        });
                    }

                } else {
                    alert('Geocode was not successful for the following reason: ' + status);
                }
            });


        });
    });
}

let adminBarsDataTableModels = {
    tableObj: null
};

let adminBarsDataTableControllers = {
    /**
     * Setup bars DataTable.
     */
    initAdminBarsDataTable: () => {
        let adminBarsDataTable = $("#adminBarsDataTable");

        //noinspection JSUnresolvedFunction
        adminBarsDataTableModels.tableObj = adminBarsDataTable.DataTable({
            orderCellsTop: true,
            columns: [
                {title: "Postion", name: "Position"},
                {title: "Bar Name", name: "Bar Name"},
                {title: "Location", name: "Location"},
                {title: "Current Bar"},
                {title: "Actions"},
            ],
            order: [[0, "asc"]],
            buttons: [
                {
                    className: "btn-color-fix",
                    text: "Add Bar",
                    action: function () {
                        adminBarsDataTableViews.renderAddModal();
                        adminBarsDataTableControllers.initAddModal();
                    }
                }
            ]
        });

        adminBarsDataTableModels.tableObj.buttons().container()
            .appendTo($(".col-sm-6:eq(0)", adminBarsDataTableModels.tableObj.table().container()));
        initDataTable(adminBarsDataTableModels.tableObj, adminBarsDataTable);
        adminBarsDataTable.find("tbody")
            .on("click", "button.editBar", function (e) {
                e.preventDefault();
                e.stopPropagation();
                let barId = $(this).closest("tr").attr("id");
                let tableObj = adminBarsDataTableModels.tableObj;
                //noinspection JSUnresolvedFunction
                let barRow = tableObj.row(`#${barId}`);
                //noinspection JSUnresolvedFunction
                let barName = tableObj.cell(barRow, tableObj.column("Bar Name:name")).data();
                //noinspection JSUnresolvedFunction
                let barLocation = tableObj.cell(barRow, tableObj.column("Location:name")).data();
                //noinspection JSUnresolvedFunction
                let barPosition = tableObj.cell(barRow, tableObj.column("Position:name")).data();
                adminBarsDataTableViews.renderEditModal(barName, barLocation, barPosition);
                adminBarsDataTableControllers.initEditModal(barId);
            })
            .on("click", "button.deleteBar", function (e) {
                e.preventDefault();
                e.stopPropagation();
                let barId = $(this).closest("tr").attr("id");
                adminBarsDataTableViews.renderDeleteModal();
                adminBarsDataTableControllers.initDeleteModal(barId);
            });

        $('input[name="currentBar"]').change(function() {

            let barId = $(this).closest("tr").attr("id");
            $.ajax({
                "url": `/bars/${barId}/update_current_bar`,
                "type": "PUT",
                "success": function (data) {
                }
            });

        });


    },
    initAddModal: function () {
        let addBarBtn = $("#addBarBtn");
        let addBarForm = $("#addBarForm");

        addBarBtn.on("click", function (e) {
            e.preventDefault();
            let addBarFormData = addBarForm.serializeArray();
            $.post("/bars", addBarFormData, function (data) {
                // growlMessage(data.result, data.message);
                adminBarsDataTableModels.tableObj.destroy();
                $("#main").html(data.template);
                adminBarsDataTableControllers.initAdminBarsDataTable();
                $("#pageModal").modal("hide");
            });
        });

    },
    initEditModal: function (barId) {
        $("#editBarBtn").on("click", function (e) {
            e.preventDefault();
            let editBarFormData = $("#editBarForm").serializeArray();
            $.ajax({
                "url": `/bars/${barId}`,
                "type": "PUT",
                "dataType": "json",
                "data": editBarFormData,
                "success": function (data) {
                    // growlMessage(data.result, data.message);
                    adminBarsDataTableModels.tableObj.destroy();
                    $("#main").html(data.template);
                    adminBarsDataTableControllers.initAdminBarsDataTable();
                    $("#pageModal").modal("hide");
                }
            });
        });

    },
    initDeleteModal: function (barId) {
        //noinspection JSUnresolvedFunction
        let barRow = adminBarsDataTableModels.tableObj.row(`#${barId}`);
        $("#deleteBarBtn").on("click", function (e) {
            e.preventDefault();
            $.ajax({
                "url": `/bars/${barId}`,
                "type": "DELETE",
                "dataType": "json",
                "success": function (data) {
                    // growlMessage(data.result, data.message);
                    adminBarsDataTableModels.tableObj.destroy();
                    $("#main").html(data.template);
                    adminBarsDataTableControllers.initAdminBarsDataTable();
                    $("#pageModal").modal("hide");
                }
            });
        });

    }

};

let adminBarsDataTableViews = {
    renderAddModal: function () {
        let pageModal = $("#pageModal");
        let pageModalBody = $("#pageModalBody");
        pageModalBody.html(`
                 <form role="form" name="addBarForm" id="addBarForm">
                <div>
                    <label class="control-label" for="barName"><strong>Bar Name</strong></label>
                    <input style="display: block; width: 100%;" id="barName" name="barName" 
                           class="form-control" type="text" value="">
                    <label class="control-label" for="location"><strong>Location</strong></label>
                    <input style="display: block; width: 100%;" id="location" name="location" 
                           class="form-control" type="text" value="">
                </div>
            </form>
            `);
        pageModal.find(".modal-title").text("Add Bar");
        pageModal.find(".modal-footer").html(`
                <button type="button" id="addBarBtn" class="btn btn-color-fix">Add</button>
                <button type="button" class="btn btn-default btn-color-fix" data-dismiss="modal">Close</button>
            `);
        pageModal.modal("show");
    },
    renderEditModal: function (barName, barLocation, barPosition) {
        let pageModal = $("#pageModal");
        let pageModalBody = $("#pageModalBody");
        pageModalBody.html(`
                 <form role="form" name="editBarForm" id="editBarForm">
                <div>
                    <label class="control-label" for="barName"><strong>Bar Name</strong></label>
                    <input style="display: block; width: 100%;" id="barName" name="barName" 
                           class="form-control" type="text" value="${barName}">
                    <label class="control-label" for="location"><strong>Location</strong></label>
                    <input style="display: block; width: 100%;" id="location" name="location" 
                           class="form-control" type="text" value="${barLocation}">
                    <label class="control-label" for="position"><strong>Position</strong></label>
                    <input style="display: block; width: 100%;" id="position" name="position" 
                           class="form-control" type="text" value="${barPosition}">
                </div>
            </form>
            `);
        pageModal.find(".modal-title").text("Update Bar");
        pageModal.find(".modal-footer").html(`
                            <button type="button" id="editBarBtn" class="btn btn-color-fix">Update</button>
                            <button type="button" class="btn btn-default btn-color-fix" data-dismiss="modal">Close</button>
                        `);
        pageModal.modal("show");
    },
    renderDeleteModal: function () {
        let pageModal = $("#pageModal");
        let pageModalBody = $("#pageModalBody");
        pageModalBody.html(`<div>Delete bar?</div>`);
        pageModal.find(".modal-title").text("Delete Bar");
        pageModal.find(".modal-footer").html(`
                            <button type="button" id="deleteBarBtn" class="btn btn-color-fix">Delete</button>
                            <button type="button" class="btn btn-default btn-color-fix" data-dismiss="modal">Close</button>
                        `);
        pageModal.modal("show");
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
                {title: "Rating", name: "Rating"},
                {title: "Group Rating"},
                {title: "Comments", name: "Comments"},
                {title: "Actions"},
            ],
            dom: "lfip",
            order: [[0, "asc"]]
        });
        initDataTable(barsDataTableModels.tableObj, barsDataTable);
        $('div.rateit, span.rateit').rateit();
        barsDataTable.find("tbody")
            .on("click", "button.editBar", function (e) {
                e.preventDefault();
                e.stopPropagation();
                let barId = $(this).closest("tr").attr("id");
                let tableObj = barsDataTableModels.tableObj;
                //noinspection JSUnresolvedFunction
                let barRow = tableObj.row(`#${barId}`);
                //noinspection JSUnresolvedFunction
                let barRating = tableObj.cell(barRow, tableObj.column("Rating:name")).nodes().to$().find('.rateit').data("rateit-value");
                //noinspection JSUnresolvedFunction
                let barComment = tableObj.cell(barRow, tableObj.column("Comments:name")).data();
                barsDataTableViews.renderEditModal(barRating, barComment);
                barsDataTableControllers.initEditModal(barId);
            });
    },
    initEditModal: function (barId) {
        $("#editBarBtn").on("click", function (e) {
            e.preventDefault();
            let editBarFormData = $("#editBarForm").serializeArray();
            $.ajax({
                "url": `/reviews/${barId}`,
                "type": "PUT",
                "dataType": "json",
                "data": editBarFormData,
                "success": function (data) {
                    // growlMessage(data.result, data.message);
                    barsDataTableModels.tableObj.destroy();
                    $("#main").html(data.template);
                    barsDataTableControllers.initBarsDataTable();
                    $("#pageModal").modal("hide");
                }
            });
        });

    }
};

let barsDataTableViews = {
    renderEditModal: function (barRating, barComment) {
        let pageModal = $("#pageModal");
        let pageModalBody = $("#pageModalBody");
        pageModalBody.html(`
                 <form role="form" name="editBarForm" id="editBarForm">
                <div>
                    <label class="control-label" for="barName"><strong>Bar Rating</strong></label>
                    <input style="display: block; width: 100%;" id="barRating" name="rating" 
                           class="form-control" type="text" value="${barRating}">
                    <label class="control-label" for="barComment"><strong>Bar Comment</strong></label>
                    <input style="display: block; width: 100%;" id="barComment" name="comments" 
                           class="form-control" type="text" value="${barComment}">
                </div>
            </form>
            `);
        pageModal.find(".modal-title").text("Update Review");
        pageModal.find(".modal-footer").html(`
                            <button type="button" id="editBarBtn" class="btn btn-color-fix">Update</button>
                            <button type="button" class="btn btn-default btn-color-fix" data-dismiss="modal">Close</button>
                        `);
        pageModal.modal("show");
    }
};

/**
 * Stops events from bubbling past a certain event.
 * @param event
 */
function stopPropagation(event) {
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
function initDataTable(table, datatable) {
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