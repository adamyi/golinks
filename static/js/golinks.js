function toggleVisibility() {
  if (document.getElementById('public-access').checked) {
    document.getElementById('visibility_div').style.display = 'none';
  } else {
    document.getElementById('visibility_div').style.display = 'block';
  }
}
