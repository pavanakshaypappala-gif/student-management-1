console.log("Student Result Management System loaded");


function validateMarks() {

    let internal =
        document.getElementById("internal");

    let external =
        document.getElementById("external");

    if (internal.value < 0 ||
        internal.value > 30) {

        alert(
            "Internal marks must be between 0 and 30"
        );

        return false;
    }

    if (external.value < 0 ||
        external.value > 70) {

        alert(
            "External marks must be between 0 and 70"
        );

        return false;
    }

    return true;
}