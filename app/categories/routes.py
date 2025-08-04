from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from app.extensions import db
from app.models import Category
from app.utils import admin_required

categories_bp = Blueprint('categories', __name__)

@categories_bp.route('/')
@admin_required
def list_categories(user):
    """List all categories"""
    try:
        categories = Category.query.order_by(Category.created_at).all()
        
        if request.is_json:
            return jsonify({
                'categories': [cat.to_dict() for cat in categories]
            }), 200
        
        return render_template('categories/list.html', categories=categories, user=user)
    
    except Exception as e:
        if request.is_json:
            return jsonify({'error': 'Failed to list categories'}), 500
        flash('Failed to load categories.', 'error')
        return render_template('categories/list.html', categories=[], user=user)

@categories_bp.route('/create', methods=['POST'])
@admin_required
def create_category(user):
    """Create a new category"""
    try:
        # Handle both JSON and form data
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
        
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        
        # Validation
        if not name:
            error = 'Category name is required'
            if request.is_json:
                return jsonify({'error': error}), 400
            flash(error, 'error')
            return redirect(url_for('categories.list_categories'))
        
        # Check if category already exists
        if Category.query.filter_by(name=name).first():
            error = 'Category with this name already exists'
            if request.is_json:
                return jsonify({'error': error}), 400
            flash(error, 'error')
            return redirect(url_for('categories.list_categories'))
        
        # Create category
        category = Category(
            name=name,
            description=description,
            is_active=True
        )
        
        db.session.add(category)
        db.session.commit()
        
        if request.is_json:
            return jsonify({
                'message': 'Category created successfully',
                'category': category.to_dict()
            }), 201
        
        flash('Category created successfully!', 'success')
        return redirect(url_for('categories.list_categories'))
        
    except Exception as e:
        db.session.rollback()
        error = 'Failed to create category. Please try again.'
        if request.is_json:
            return jsonify({'error': error}), 500
        flash(error, 'error')
        return redirect(url_for('categories.list_categories'))

@categories_bp.route('/<int:category_id>/update', methods=['POST'])
@admin_required
def update_category(user, category_id):
    """Update a category"""
    try:
        category = Category.query.get_or_404(category_id)
        
        # Handle both JSON and form data
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
        
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        is_active = data.get('is_active', True)
        
        # Convert string boolean to actual boolean
        if isinstance(is_active, str):
            is_active = is_active.lower() in ['true', '1', 'yes', 'on']
        
        # Validation
        if not name:
            error = 'Category name is required'
            if request.is_json:
                return jsonify({'error': error}), 400
            flash(error, 'error')
            return redirect(url_for('categories.list_categories'))
        
        # Check if another category with this name exists
        existing = Category.query.filter_by(name=name).first()
        if existing and existing.id != category_id:
            error = 'Category with this name already exists'
            if request.is_json:
                return jsonify({'error': error}), 400
            flash(error, 'error')
            return redirect(url_for('categories.list_categories'))
        
        # Update category
        category.name = name
        category.description = description
        category.is_active = is_active
        
        db.session.commit()
        
        if request.is_json:
            return jsonify({
                'message': 'Category updated successfully',
                'category': category.to_dict()
            }), 200
        
        flash('Category updated successfully!', 'success')
        return redirect(url_for('categories.list_categories'))
        
    except Exception as e:
        db.session.rollback()
        error = 'Failed to update category. Please try again.'
        if request.is_json:
            return jsonify({'error': error}), 500
        flash(error, 'error')
        return redirect(url_for('categories.list_categories'))

@categories_bp.route('/<int:category_id>/delete', methods=['POST'])
@admin_required
def delete_category(user, category_id):
    """Delete a category (soft delete by setting is_active=False)"""
    try:
        category = Category.query.get_or_404(category_id)
        
        # Check if category has tickets
        if category.tickets.count() > 0:
            error = 'Cannot delete category with existing tickets. Deactivate it instead.'
            if request.is_json:
                return jsonify({'error': error}), 400
            flash(error, 'error')
            return redirect(url_for('categories.list_categories'))
        
        # Soft delete by setting is_active=False
        category.is_active = False
        
        db.session.commit()
        
        if request.is_json:
            return jsonify({'message': 'Category deactivated successfully'}), 200
        
        flash('Category deactivated successfully!', 'success')
        return redirect(url_for('categories.list_categories'))
        
    except Exception as e:
        db.session.rollback()
        error = 'Failed to delete category. Please try again.'
        if request.is_json:
            return jsonify({'error': error}), 500
        flash(error, 'error')
        return redirect(url_for('categories.list_categories'))