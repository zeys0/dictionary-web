function save_word() {
  for (let i = 0; i < defs.length; i++) {
    let def = defs[i];
    let category = def.fl;
    let shortdef = def.shortdef[0];
    let date = def.date;

    defs[i] = {
      category: category,
      shortdef: shortdef,
      date: date,
    };
  }

  let data = {
    word_give: word,
    definitions_give: defs,
  };

  $.ajax({
    type: "POST",
    url: "/api/save_word",
    data: JSON.stringify(data),
    headers: {
      "Content-Type": "application/json",
    },
    success: function (response) {
      if (response.result === "success") {
        alert(response.msg);
        window.location.href = `/detail/${word}?status_give=old`;
      } else {
        alert("something error");
      }
    },
  });
}

function delete_word() {
  $.ajax({
    type: "POST",
    url: "/api/delete_word",
    data: { word },
    success: function (response) {
      if (response.result === "success") {
        alert(response.msg);
        window.location.href = `/detail/${word}?status_give=new`;
      } else {
        alert("something error");
      }
    },
  });
}

function find_word() {
  let word = $("#input-word").val().toLowerCase().trim();
  if (!word) {
    alert("Please type a word");
    return;
  }
  if (word_list.includes(word)) {
    let row = $(`#word-${word}`);
    row.addClass("highlight");
    row.siblings().removeClass("highlight");
    row[0].scrollIntoView();
  } else {
    window.location.href = `/detail/${word}?status_give=new`;
  }
}

function get_examples() {
  let list = $("#example-list");
  list.empty();
  $.ajax({
    type: "GET",
    url: `/api/get_exs?word=${word}`,
    data: {},
    success: function (response) {
      console.log(response);
      if (response.result === "success") {
        let examples = response.examples;
        let temp_html = ``;
        for (let i = 0; i < examples.length; i++) {
          let example = examples[i];
          let id = example.id;
          let sentence = example.example;
          temp_html += ` <li>
        ${sentence}&nbsp;&nbsp;&nbsp;<a
            href="javascript:delete_ex('${id}')"
            >delete</a
          >
        </li>`;
        }
        list.append(temp_html);
      }
    },
  });
}

function add_ex() {
  let new_ex = $("#new-example").val();
  console.log(new_ex);
  $.ajax({
    type: "POST",
    url: `/api/save_ex`,
    data: {
      example: new_ex,
      word: word,
    },
    success: function (response) {
      console.log(response);
      if (response.result === "success") {
        alert(response.msg);
        get_examples();
      }
    },
  });
}

function delete_ex(id) {
  console.log("deleting", id);
  $.ajax({
    type: "POST",
    url: `/api/delete_ex`,
    data: {
      word: word,
      id: id,
    },
    success: function (response) {
      if (response.result === "success") {
        alert(response.msg);
      }
      get_examples();
    },
  });
}
