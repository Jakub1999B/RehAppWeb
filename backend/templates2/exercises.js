//// exercises.js
//document.addEventListener('DOMContentLoaded', () => {
//    const exercises = document.querySelectorAll('.exercise');
//
//    exercises.forEach(exercise => {
//        exercise.addEventListener('click', () => {
//            exercise.querySelector('.exercise-details').classList.toggle('show');
//        });
//    });
//});

document.addEventListener('DOMContentLoaded', () => {
    const exercises = document.querySelectorAll('.exercise');

    exercises.forEach(exercise => {
        const arrow = exercise.querySelector('.arrow'); // Select the arrow within the exercise
        const exerciseDetails = exercise.querySelector('.exercise-details');

        exercise.addEventListener('click', () => {
            exerciseDetails.classList.toggle('show');
            arrow.classList.toggle('rotate'); // Toggle the rotate class on the arrow
        });
    });
});



