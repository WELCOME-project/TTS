$( document ).ready(function() {

  //webkitURL is deprecated but nevertheless 
  URL = window.URL || window.webkitURL;

  var gumStream;
  //stream from getUserMedia() 
  var rec;
  //Recorder.js object 
  var input;

  var recordedBlob;

  //MediaStreamAudioSourceNode we'll be recording 
  // shim for AudioContext when it's not avb. 
  var AudioContext = window.AudioContext || window.webkitAudioContext;
  var audioContext = new AudioContext;

  //new audio context to help us record 
  var recordButton = document.getElementById("recordButton");
  var recordPlayer = document.getElementById("recordPlayer");
  var sourceSelect = document.getElementById("selectSourceLanguage");

  var recogniseButton = document.getElementById("recogniseButton");
  recogniseButton.disabled = true;

  var translateInput = document.getElementById("translateInput");
  var translateButton = document.getElementById("translateButton");
  //translateButton.disabled = true;

  var synthesizeInput = document.getElementById("synthesizeInput");
  var synthesizeButton = document.getElementById("synthesizeButton");
  var synthesizedPlayer = document.getElementById("synthesizedPlayer");
  //synthesizeButton.disabled = true;

  var processButton = document.getElementById("processButton");

  //add events to those 3 buttons 
  recordButton.addEventListener("click", toggleRecord);

  recogniseButton.addEventListener("click", postRecognise);

  translateButton.addEventListener("click", postTranslate);

  synthesizeButton.addEventListener("click", postSynthesis);

  processButton.addEventListener("click", postProcess);

  function retrieveLanguages() {
    $.ajax({
      type: 'GET',
      url: '/available_languages'

    }).done(function (data) {
      console.log("Retrieved available languages!");

      var $sourceSelect = $(sourceSelect);
      $sourceSelect.find('option').remove();
      $.each(data["speech2text"], function(index, value) 
      {
          $sourceSelect.append('<option value=' + value + '>' + value.toUpperCase() + '</option>');
      }); 

    }).fail(function(jqXHR, textStatus, errorThrown ) {
      alertError(jqXHR, textStatus, errorThrown);
    });

  }
  retrieveLanguages();

  function toggleRecord() {
    if ($(this).attr("aria-pressed") === "false") {
      startRecording();
    } else {
      stopRecording();
    }
  }

  function startRecording() {

    console.log("startButton clicked");
    audioContext.resume().then(function () {

      if (navigator.mediaDevices === undefined) {

        alert("Unable to access mediaDevices! Maybe the current document isn't loaded securely?")

      } else {

        var constraints = {
          audio: true,
          video: false
        }

        recordButton.innerText = "Stop recording";
        recogniseButton.disabled = true;

        /* We're using the standard promise based getUserMedia()
        
        https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia */

        navigator.mediaDevices.getUserMedia(constraints)
          .then(function (stream) {
            console.log("getUserMedia() success, stream created, initializing Recorder.js ...");
            /* assign to gumStream for later use */
            gumStream = stream;
            /* use the stream */
            input = audioContext.createMediaStreamSource(stream);
            /* Create the Recorder object and configure to record mono sound (1 channel) Recording 2 channels will double the file size */
            rec = new Recorder(input, {
              numChannels: 1
            })
            //start the recording process 
            rec.record()
            console.log("Recording started");
    
          }).catch(function (err) {
            console.log("Something happened while recording: " + err);
          });
      }
    });
  }

  function stopRecording() {
    console.log("stopButton clicked");

    //tell the recorder to stop the recording 
    rec.stop(); //stop microphone access 
    gumStream.getAudioTracks()[0].stop();

    rec.exportWAV(blob => {
      recordedBlob = blob;
      recordPlayer.src = URL.createObjectURL(blob);
    });

    recordButton.innerText = "Start recording";
    recogniseButton.disabled = false;
  }
  
  function alertError(jqXHR, status, message) {
    let data = jqXHR.responseJSON;

    let alertMessage = "";
    if (data && data.detail && data.detail.customData) {
      let customData = data.detail.customData;
      alertMessage = customData.module + " module error: " + customData.message;
    } else {
      alertMessage = message + " (Status: " + jqXHR.status +")";
    }

    let errorPanel = $('#errorAlert');
    errorPanel.append("<p>" + alertMessage + "</p>").slideDown();

    setTimeout(function() { 
      errorPanel.slideUp({
        always: function() { $('p:last-child', errorPanel).remove(); }
      });
    }, 5000);
  }

  function postRecognise() {

    let formData = new FormData();
    formData.append('language', sourceSelect.value);
    formData.append('audio', recordedBlob, "recorded.wav");

    $.ajax({
      type: 'POST',
      url: '/recognise_audio',
      data: formData,
      processData: false,
      contentType: false,
      beforeSend: function () {
        translateInput.innerHTML = "<img src=\"./static/images/ajax-loader.gif\" width=\"16\" height=\"16\"></img>";
        recogniseButton.disabled = true;
      }

    }).done(function (data) {
      console.log("Speech-to-text response received!");
      translateInput.innerText = data.text;

    }).fail(function(jqXHR, textStatus, errorThrown ) {
      translateInput.innerHTML = "";
      alertError(jqXHR, textStatus, errorThrown);

    }).always(function() {
      recogniseButton.disabled = false;
    });
  }

  function postTranslate() {

    let formData = new FormData();
    formData.append("source_language", sourceSelect.value);
    formData.append("target_language", "en");
    const text = translateInput.innerHTML.replace(/<div>/g,"\n").replace(/<\/div>/g,"").replace(/<br>/g,"\n");
    formData.append("text", text);

    $.ajax({
      type: 'POST',
      url: './translate',
      data: formData,
      processData: false,
      contentType: false,
      beforeSend: function () {
        synthesizeInput.innerHTML = "<img src=\"./static/images/ajax-loader.gif\" width=\"16\" height=\"16\"></img>";
        translateButton.disabled = true;
      }

    }).done(function (data) {
      console.log("Translation response received!");
      synthesizeInput.innerText = data.text;

    }).fail(function(jqXHR, textStatus, errorThrown ) {
      synthesizeInput.innerHTML = "";
      alertError(jqXHR, textStatus, errorThrown);

    }).always(function() {
      translateButton.disabled = false;
    });
  }

  function postSynthesis() {

    let formData = new FormData();
    const text = synthesizeInput.innerHTML.replace(/<div>/g,"\n").replace(/<\/div>/g,"").replace(/<br>/g,"\n");
    formData.append("text", text);

    $.ajax({
      type: 'POST',
      url: '/synthesize_text',
      cache: false,
      xhrFields:{
          responseType: 'blob'
      },
      data: formData,
      processData: false,
      contentType: false,
      beforeSend: function () {
        synthesizeButton.disabled = true;
      }

    }).done(function (data) {
      console.log("Synthesis response received!");
      let url = window.URL || window.webkitURL;
      synthesizedPlayer.src = url.createObjectURL(data);

    }).fail(function(jqXHR, textStatus, errorThrown ) {
      alertError(jqXHR, textStatus, errorThrown);

    }).always(function() {
      synthesizeButton.disabled = false;
    });
  }

  function postProcess() {

    let formData = new FormData();
    formData.append('audio', recordedBlob, "recorded.wav");
    formData.append("source_language", sourceSelect.value);
    formData.append("target_language", "en");

    var originalText = $(processButton).text();
    var waitingText = "Translating... <img src=\"./static/images/ajax-loader.gif\" width=\"16\" height=\"16\"></img>";

    $.ajax({
      type: 'POST',
      url: '/process',
      cache: false,
      xhrFields:{
          responseType: 'blob'
      },
      data: formData,
      processData: false,
      contentType: false,
      beforeSend: function () {
        processButton.innerHTML = waitingText;
        processButton.disabled = true;
      }

    }).done(function (data) {
      console.log("Process response received!");
      let url = window.URL || window.webkitURL;
      synthesizedPlayer.src = url.createObjectURL(data);

    }).fail(function(jqXHR, textStatus, errorThrown ) {
      alertError(jqXHR, textStatus, errorThrown);
    
    }).always(function() {
      processButton.innerHTML = originalText;
      processButton.disabled = false;
    });
  }

  $('[data-toggle-secondary]').each(function() {
    var $toggle = $(this);
    var originalText = $toggle.text();
    var secondaryText = $toggle.data('toggle-secondary');
    var $target = $($toggle.data('target'));

    $target.on('show.bs.collapse hide.bs.collapse', function() {
        if ($toggle.text() == originalText) {
            $toggle.text(secondaryText);
        } else {
            $toggle.text(originalText);
        }
    });
  });

});