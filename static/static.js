

const newcart = document.createElement('div')

codeBlock = '<a href=" {% url "ecommerce:product-list" object.slug %} " class="btn btn-warning" id="cart">' +
                '<span class="material-symbols-outlined">add</span>' +
            '</a>' +
            '<span>{{num}} </span>' +
            '<a href="{{object.get_remove_one_item}} " class="btn btn-warning" id="cart">' +
                '<span class="material-symbols-outlined">remove</span>' +
            '</a>'
            

newcart.innerHTML = codeBlock

const buttonall = document.querySelectorAll("#cart")
const parent = buttonall.parentNode;

function getquantity(){
    for (let index = 0; index < buttonall.length; index++) {
        buttonall[index].addEventListener('click', () => {
            // alert('hi');
            buttonall.parentNode.replaceChild(newcart, buttonall);
            
        
        });
        
    } 
}



// buttonall.forEach((button) => {
//     button.addEventListener('click', () => {
//         button.replaceWith(newcart);
//         console.log("it worked")

//     });
// });






// function getquantity() {
//     const buttonall = document.querySelectorAll(".btn .btn-warning")
//     const newcart = document.createElement('div')

//     codeBlock = '<a href="{{object.get_add_to_cart_url}} " class="btn btn-warning" id="cart">' +
//                     '<span class="material-symbols-outlined">add</span>' +
//                 '</a>' +
//                 '<span>{{num}} </span>' +
//                 '<a href="{{object.get_remove_one_item}} " class="btn btn-warning" id="cart">' +
//                     '<span class="material-symbols-outlined">remove</span>' +
//                 '</a>'

//     newcart.innerHTML = codeBlock

//     for (let index = 0; index < buttonall.length; index++) {
//         const element = buttonall[index];
//         element.replaceWith(newcart);
        
//     }

// }








// const links = document.querySelectorAll('a')

// links.forEach(link => {
//   const replacement = document.createElement('span')
  
//   // copy attributes
//   for (let i = 0; i < link.attributes.length; i++) {
//      const attr = link.attributes[i]
//      replacement.setAttribute(attr.name, attr.value)
//   }
  
//   // copy content
//   replacement.innerHTML = link.innerHTML
  
//   // or you can use appendChild instead
//   // link.childNodes.forEach(node => replacement.appendChild(node))

//   link.replaceWith(replacement)
// })





// var codeBlock = '<div class="content">' +
//                         '<h1>This is a heading</h1>' +
//                         '<p>This is a paragraph of text.</p>' +
//                         '<p><strong>Note:</strong> If you don\'t escape "quotes" properly, it will not work.</p>' +
//                     '</div>';

//     // Inserting the code block to wrapper element
// document.getElementById("wrapper").innerHTML = codeBlock







// <script>
//     var newhtml = '<header class="fl-page-header fl-page-header-fixed fl-page-nav-right"><div class="fl-page-header-wrap"><div class="fl-page-header-container container"><div class="fl-page-header-row row"><div class="fl-page-logo-wrap col-md-3 col-sm-12"><div class="fl-page-header-logo"><a href="https://aaendo.wpengine.com/patients/"><img class="fl-logo-img" itemscope itemtype="http://schema.org/ImageObject" src="https://aaendo.wpengine.com/patients/wp-content/uploads/sites/3/2017/08/American-Association-of-Endodontists-1.png" data-retina="https://aaendo.wpengine.com/patients/wp-content/uploads/sites/3/2017/08/American-Association-of-Endodontists@2x.png" alt="Endodontists: Specialists in Saving Teeth" /><img class="sticky-logo fl-logo-img" itemscope itemtype="http://schema.org/ImageObject" src="https://aaendo.wpengine.com/patients/wp-content/uploads/sites/3/2017/08/American-Association-of-Endodontists-1.png"alt="Endodontists: Specialists in Saving Teeth" /><meta itemprop="name" content="Endodontists: Specialists in Saving Teeth" /></a></div></div><div class="fl-page-fixed-nav-wrap col-md-9 col-sm-12"><div class="fl-page-nav-wrap"><nav class="fl-page-nav fl-nav navbar navbar-default"><div class="fl-page-nav-collapse collapse navbar-c'

//     $('header').replaceWith(newhtml);
// </script>