function getActiveTokensCall() {
    blockScreen();
	getActiveTokens("getActiveTokensBack");
}

function getActiveTokensBack(result) {
    unblockScreen();
    if (result['code'] === "500") {
        alert(result['message']);
    } else if (result['code'] === "200") {
        var listOfTokens = result['responseObject'];
        $('#storageSelect').empty();
        $('#storageSelect').append('<option value="PKCS12">PKCS12</option>');
        for (var i = 0; i < listOfTokens.length; i++) {
            $('#storageSelect').append('<option value="' + listOfTokens[i] + '">' + listOfTokens[i] + '</option>');
        }
    }
}

function getKeyInfoCall() {
    blockScreen();
    getKeyInfo("PKCS12", "getKeyInfoBack");
}

function getKeyInfoBack(result) {
    unblockScreen();
    if (result['code'] === "500") {
        alert(result['message']);
    } else if (result['code'] === "200") {
        var res = result['responseObject'];

        var subjectCn = res['subjectCn'];
        $("#subjectCn").val(subjectCn);

        var subjectDn = res['subjectDn'];
        $("#subjectDn").val(subjectDn);
    }
}

function signXmlCall() {
    var xmlToSign = $("#xmlToSign").val();
	blockScreen();
    signXml("PKCS12", "SIGNATURE", xmlToSign, "signXmlBack");
}

function signXmlBack(result) {
	unblockScreen();
    if (result['code'] === "500") {
        alert(result['message']);
    } else if (result['code'] === "200") {
        var res = result['responseObject'];
        $("#signedXml").val(res);
    }
}

function createCMSSignatureFromFileCall() {
    var selectedStorage = $('#storageSelect').val();
    var flag = $("#flag").is(':checked');
    var filePath = $("#filePath").val();
    if (filePath !== null && filePath !== "") {
		blockScreen();
        createCMSSignatureFromFile(selectedStorage, "SIGNATURE", filePath, flag, "createCMSSignatureFromFileBack");
    } else {
        alert("Не выбран файл для подписи!");
    }
}

function createCMSSignatureFromFileBack(result) {
	unblockScreen();
    if (result['code'] === "500") {
        alert(result['message']);
    } else if (result['code'] === "200") {
        var res = result['responseObject'];
        $("#createdCMS").val(res);
    }
}

function createCMSSignatureFromBase64Call() {
    var selectedStorage = $('#storageSelect').val();
    var flag = $("#flagForBase64").is(':checked');
    var base64ToSign = $("#base64ToSign").val();
    if (base64ToSign !== null && base64ToSign !== "") {
		$.blockUI();
        createCMSSignatureFromBase64(selectedStorage, "SIGNATURE", base64ToSign, flag, "createCMSSignatureFromBase64Back");
    } else {
        alert("Нет данных для подписи!");
    }
}

function createCMSSignatureFromBase64Back(result) {
	$.unblockUI();
    if (result['code'] === "500") {
        alert(result['message']);
    } else if (result['code'] === "200") {
        var res = result['responseObject'];
        $("#createdCMSforBase64").val(res);
    }
}

function showFileChooserCall() {
    blockScreen();
    showFileChooser("ALL", "", "showFileChooserBack");
}

function showFileChooserBack(result) {
    unblockScreen();
    if (result['code'] === "500") {
        alert(result['message']);
    } else if (result['code'] === "200") {
        var res = result['responseObject'];
        $("#filePath").val(res);
    }
}

function changeLocaleCall() {
    var selectedLocale = $('#localeSelect').val();
    changeLocale(selectedLocale);
}
