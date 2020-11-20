import React, { useState, useEffect } from 'react';
import { Button } from 'reactstrap'
import { useHistory } from 'react-router-dom';

import LabelWithButtons from '../../components/LabelWithButtons/LabelWithButtons';
import LabelWithSelect from '../../components/LabelWithSelect/LabelWithSelect';

import SHIRTS from '../../shared/shirts';
import './DetailsPage.css';
import { generateShirtProps, getDefaultShirt, updateDetailsState } from '../../shared/shirtHelpers';
import { colorCapitalize } from '../../shared/colorHelpers';
import { shirtSizes, shirtQuantities } from '../../shared/shirtConstants';

const DetailsPage = (props) => {
    const { detailsState, setDetailsState, selectedShirt, addNewCartItem } = props;
    const shirtIdx = selectedShirt;
    const shirtProps = generateShirtProps(SHIRTS[shirtIdx], shirtIdx);
    const history = useHistory();

    // Props for Options
    let colorButtonProps = [];
    for (const color of Object.keys(shirtProps.colors)){
        colorButtonProps.push({
            title: colorCapitalize(color),
            fillColor: color,
            returnVal: color,
            disabled: false,
        });
    };
    
    // Initial Values
    let sideInitial = "front";
    let colorInitial = getDefaultShirt(shirtProps.colors).key;
    let pathInitial = shirtProps.displayShirtPath;
    let sizeInitial = shirtSizes[0];
    let quantityInitial = shirtQuantities[0];
    if (detailsState.idx === shirtIdx) {
        sideInitial = detailsState.shirtSide;
        colorInitial = detailsState.shirtColor;
        pathInitial = detailsState.shirtPath;
        sizeInitial = detailsState.shirtSize;
        quantityInitial = detailsState.shirtQuantity;
    }

    // State Variables
    const [shirtSide, setShirtSide] = useState(sideInitial);
    const [shirtColor, setShirtColor] = useState(colorInitial);
    const [shirtPath, setShirtPath] = useState(pathInitial);
    const [shirtSize, setShirtSize] = useState(sizeInitial);
    const [shirtQuantity, setShirtQuantity] = useState(quantityInitial);

    const [sideButtonProps, setSideButtonProps] = useState([
        {title: "Front", fillColor: "generic-red", returnVal: "front", disabled: false,},
        {title: "Back", fillColor: "generic-red", returnVal: "back", disabled: false,}
    ]);

    useEffect(() => {
        if(shirtColor !== "No colors available") {
            updateDetailsState(shirtProps, shirtColor, shirtSide, sideButtonProps, setShirtSide, setShirtPath, setSideButtonProps);
        }
        else {
            setShirtPath(shirtProps.defaultFront);
        }
    }, [shirtSide, shirtColor, shirtProps, sideButtonProps]);

    const [canAddToCart, setCanAddToCart] = useState(false);
    useEffect(() => {
        if (shirtSize === shirtSizes[0] || shirtProps.price === "Out-Of-Stock" || shirtColor === "No colors available") {
            setCanAddToCart(false);
        }
        else {
            setCanAddToCart(true);
        }
    }, [shirtProps, shirtSize, shirtColor]);

    // Update details state
    useEffect(() => {
        setDetailsState({
            idx: shirtIdx,
            shirtSide: shirtSide,
            shirtColor: shirtColor,
            shirtPath: shirtPath,
            shirtSize: shirtSize,
            shirtQuantity: shirtQuantity,
        });
    }, [shirtIdx, shirtSide, shirtColor, shirtPath, shirtSize, shirtQuantity, setDetailsState]);

    const addToCart = () => {
        const newItem = {
            name: shirtProps.name,
            displayImage: getDisplayImage(),
            quantity: parseInt(shirtQuantity),
            color: colorCapitalize(shirtColor),
            size: shirtSize,
            price: parseFloat(shirtProps.price.slice(1)),
            shirtIdx: shirtIdx,
            shirtType: "existing",
        }
        addNewCartItem(newItem);
        history.push('/cart')
    }

    const getDisplayImage = () => {
        let image = shirtProps.colors[shirtColor].front;
        if (!shirtProps.colors[shirtColor].front){
            image = shirtProps.defaultFront
        }
        return image;
    }

    return (
        <div className="DetailsPage__container">
            <div className="DetailsPage__content">
                <h1>{shirtProps.name}</h1>
                <div className="DetailsPage__shirt-container">
                    <img className="DetailsPage__image" src={shirtPath} alt={shirtProps.name}></img>
                    <div className="DetailsPage__shirt-options">
                        <h1 className="DetailsPage__price">{shirtProps.price}</h1>
                        <p className="DetailsPage__description">{shirtProps.description}</p>
                        <LabelWithButtons label="Side" buttons={sideButtonProps} setButtonOption={setShirtSide}/>
                        <LabelWithButtons label="Color" buttons={colorButtonProps} setButtonOption={setShirtColor}/>
                        <LabelWithSelect label="Quantity" range={shirtQuantities} selectedOption={shirtQuantity} setSelectOption={setShirtQuantity} />
                        <LabelWithSelect label="Size" range={shirtSizes} selectedOption={shirtSize} setSelectOption={setShirtSize} />
                        <Button onClick={addToCart} className="DetailsPage__cart-button" disabled={!canAddToCart}>Add To Cart</Button>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default DetailsPage;