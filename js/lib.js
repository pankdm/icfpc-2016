function tableCell(text) {
  return '<td>' + text + '</td>';
}
function tableRow(text) {
  return '<tr>' + text + '</tr>';
}

String.format = function() {
    // The string containing the format items (e.g. "{0}")
    // will and always has to be the first argument.
    var theString = arguments[0];
    // start with the second argument (i = 1)
    for (var i = 1; i < arguments.length; i++) {
        // "gm" = RegEx options for Global search (more than one instance)
        // and for Multiline search
        var regEx = new RegExp("\\{" + (i - 1) + "\\}", "gm");
        theString = theString.replace(regEx, arguments[i]);
    }
    return theString;
}


function addElement(table, problem, our_approx_map) {
  var n = 0
  row = ''
  attempts = 0


  // other than 1.0
  max_res = 0
  sum_res = 0.0
  console.log(problem)
  for (j in problem['ranking']) {
    r = problem['ranking'][j];
    // console.log(r['resemblance'])
    res = r['resemblance']
    if (res == 1.0) {
      n += 1
    } else {
      if (res > max_res) {
        max_res = res
      }
    }
    attempts += 1
  }

  for (j in problem['ranking']) {
    r = problem['ranking'][j];
    res = r['resemblance']
    if (res != 1.0) {
      sum_res += res
    }
  }
  // console.log(num_max_res)



  number += 1
  row += tableCell(number)

  p_id = problem['problem_id'];
  id_link = String.format('<a href=http://2016sv.icfpcontest.org/problem/view/{0} > {1}',
    p_id,
    p_id
  )
  row += tableCell(id_link);

  pt = problem['publish_time']
  tz = new Date(pt * 1000)
  row += tableCell(tz)

  row += tableCell(n)

  attempts =
  row += tableCell(attempts)
  row += tableCell(problem['problem_size'])
  s = problem['solution_size']
  row += tableCell('<b>' + s + '</b>')

  score_for_solve = s / (n + 2)
  row += tableCell(score_for_solve.toFixed(2))

  score_for_approx = s / (n + 2) / sum_res * max_res
  row += tableCell(score_for_approx.toFixed(2))

  row += tableCell(max_res)

  our_approx = our_approx_map[p_id]
  row += tableCell(our_approx)

  score_for_our_approax = s / (n + 2) / sum_res * our_approx
  row += tableCell(score_for_our_approax.toFixed(2))


  img = String.format(
      '<a href="img/t{0}.png"> <img src="img/t{0}.png" width=30% height=30%> </a>', p_id);
  row += tableCell(img);

  table.append(tableRow(row))

  total_score += (5000 - s) / (n + 1)
}

function countScores(data) {
  by_owner = {}
  for (i in data['problems']) {
    n = 0
    p = data['problems'][i];

    for (j in p['ranking']) {
      r = p['ranking'][j];
      res = r['resemblance']
      if (res == 1.0) {
        n += 1
      }
    }


    s = p['solution_size']
    score = (5000 - s) / (n + 1)
    owner = p['owner']
    if (owner in by_owner) {
      by_owner[owner] += score
    } else {
      by_owner[owner] = score
    }
  }
  console.log(by_owner)
  return by_owner
}

function initTable(table) {
  table.append('<tr>' +
    '<td> Number </td>' +
    '<td> Problem id </td>' +
    '<td> Publish time </td>' +
    '<td> Num solved </td>' +
    '<td> Attempts </td>' +
    '<td> Problem size </td>' +
    '<td> Solution size </td>' +
    '<td> Score for solve </td>' +
    '<td> Score for best approx </td>' +
    '<td> Best approx </td>' +
    '<td> Our approx </td>' +
    '<td> Score for our approx </td>' +
    '<td> Image </td>' +
  '</tr>'
  );
}

function renderTableByList(data, list, our_scores, predicat) {
  all_problems = {}
  for (i in data['problems']) {
    problem = data['problems'][i];
    all_problems[ problem['problem_id'] ] = problem
  }



  table = $('#scores')
  initTable(table)

  total_score = 0
  number = 0
  LIMIT = 1000

  for (i in list) {
    p_id = list[i];
    if (!(p_id in all_problems)) {
      continue;
    }

    problem = all_problems[p_id]
    // console.log(p_id)
    // console.log(problem)

    if (predicat(problem) === false) {
      continue;
    }

    addElement(table, problem, our_scores)

    if (number >= LIMIT) {
      break;
    }
  }


}

function getUrlVars() {
  var vars = {};
  var parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(m,key,value) {
    vars[key] = value;
  });
  return vars;
}


function renderTable(data, predicat) {
  table = $('#scores')
  initTable(table)

  total_score = 0
  number = 0
  LIMIT = 50

  for (i in data['problems']) {
    problem = data['problems'][i];
    if (predicat(problem) === false) {
      continue;
    }

    addElement(table, problem, {})

    if (number >= LIMIT) {
      break;
    }
  }
  $('#total_score').html('Score from submitted problems: ' + total_score)
}
